"""
Regulator-only operations for audit, batch locking, and MRV overrides
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.accounts.models import UserProfile, AuditLog
from apps.api.permissions import IsRegulator, IsNotFrozen
from apps.registry.models import CreditBatch
from apps.mrv.models import MRVRequest


class RegulatorViewSet(viewsets.ViewSet):
    """Regulator-only operations"""
    permission_classes = [IsAuthenticated, IsRegulator, IsNotFrozen]
    
    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        """Get audit logs (regulator view)"""
        # Filters
        user_id = request.query_params.get('user_id')
        action_type = request.query_params.get('action')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        logs = AuditLog.objects.all()
        
        if user_id:
            logs = logs.filter(user_profile__id=user_id)
        if action_type:
            logs = logs.filter(action=action_type)
        if date_from:
            logs = logs.filter(created_at__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__lte=date_to)
        
        logs = logs.order_by('-created_at')[:100]  # Latest 100
        
        return Response([
            {
                'id': str(log.id),
                'user_email': log.user_profile.email if log.user_profile else 'N/A',
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'description': log.description,
                'created_at': log.created_at.isoformat(),
            }
            for log in logs
        ])
    
    @action(detail=False, methods=['patch'], url_path='lock-batch')
    def lock_batch(self, request):
        """Lock a registry batch (regulator action)"""
        batch_id = request.data.get('batch_id')
        reason = request.data.get('reason', 'Regulatory action')
        
        try:
            batch = CreditBatch.objects.get(id=batch_id)
            
            # Check if batch is locked
            if hasattr(batch, 'is_locked') and batch.is_locked:
                return Response(
                    {'error': 'Batch already locked'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Lock the batch
            if hasattr(batch, 'is_locked'):
                batch.is_locked = True
                batch.locked_by = UserProfile.objects.get(django_user_id=str(request.user.id))
                batch.locked_reason = reason
                batch.locked_at = timezone.now()
                batch.save()
            
            # Log audit trail
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            AuditLog.objects.create(
                user_profile=profile,
                action='LOCK_BATCH',
                resource_type='CreditBatch',
                resource_id=str(batch.id),
                description=f'Batch locked by regulator: {reason}'
            )
            
            return Response({'message': 'Batch locked successfully'})
        except CreditBatch.DoesNotExist:
            return Response(
                {'error': 'Batch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'], url_path='unlock-batch')
    def unlock_batch(self, request):
        """Unlock a registry batch (regulator action)"""
        batch_id = request.data.get('batch_id')
        reason = request.data.get('reason', 'Regulatory decision')
        
        try:
            batch = CreditBatch.objects.get(id=batch_id)
            
            # Check if batch is locked
            if not (hasattr(batch, 'is_locked') and batch.is_locked):
                return Response(
                    {'error': 'Batch is not locked'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Unlock the batch
            if hasattr(batch, 'is_locked'):
                batch.is_locked = False
                batch.unlocked_by = UserProfile.objects.get(django_user_id=str(request.user.id))
                batch.unlocked_reason = reason
                batch.unlocked_at = timezone.now()
                batch.save()
            
            # Log audit trail
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            AuditLog.objects.create(
                user_profile=profile,
                action='UNLOCK_BATCH',
                resource_type='CreditBatch',
                resource_id=str(batch.id),
                description=f'Batch unlocked by regulator: {reason}'
            )
            
            return Response({'message': 'Batch unlocked successfully'})
        except CreditBatch.DoesNotExist:
            return Response(
                {'error': 'Batch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'], url_path='override-mrv')
    def override_mrv(self, request):
        """Override MRV request (regulator action)"""
        mrv_id = request.data.get('mrv_request_id')
        override_decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        reason = request.data.get('reason', 'Regulatory override')
        
        try:
            mrv = MRVRequest.objects.get(id=mrv_id)
            
            # Set override
            mrv.regulatory_override = override_decision
            mrv.override_reason = reason
            mrv.override_by = UserProfile.objects.get(django_user_id=str(request.user.id))
            mrv.override_at = timezone.now()
            mrv.save()
            
            # Log audit trail
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            AuditLog.objects.create(
                user_profile=profile,
                action='MRV_OVERRIDE',
                resource_type='MRVRequest',
                resource_id=str(mrv.id),
                description=f'MRV overridden to {override_decision}: {reason}'
            )
            
            return Response({'message': f'MRV request overridden to {override_decision}'})
        except MRVRequest.DoesNotExist:
            return Response(
                {'error': 'MRV request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
