"""
Projects views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime

from apps.projects.models import (
    Project, CarbonCategory, ProjectMethodology
)
from apps.projects.serializers import (
    ProjectSerializer, CarbonCategorySerializer, ProjectMethodologySerializer
)
from apps.mrv.models import MRVRequest


class CarbonCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for carbon categories"""
    permission_classes = [IsAuthenticated]
    serializer_class = CarbonCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']
    
    def get_queryset(self):
        return CarbonCategory.objects()


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for carbon projects"""
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'carbon_category', 'organization']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'baseline_emissions']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get projects visible to user"""
        # In production, filter by organization membership
        return Project.objects()
    
    def perform_create(self, serializer):
        """Create project"""
        project_data = serializer.validated_data
        carbon_category = CarbonCategory.objects.get(id=project_data['carbon_category_id'])
        
        project = Project(
            name=project_data['name'],
            description=project_data.get('description'),
            carbon_category=carbon_category,
            baseline_emissions=project_data.get('baseline_emissions'),
            target_reduction=project_data.get('target_reduction'),
            status='DRAFT',
            created_by_email=self.request.user.email,
        )
        project.save()
    
    @action(detail=True, methods=['post'])
    def submit_mrv(self, request, pk=None):
        """Submit project for MRV"""
        project = Project.objects.get(id=pk)
        
        if project.status != 'DRAFT':
            return Response(
                {'error': 'Only draft projects can be submitted for MRV'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create MRV request
        mrv_request = MRVRequest(
            project=project,
            requested_by_email=request.user.email,
            reporting_period_start=request.data.get('reporting_period_start'),
            reporting_period_end=request.data.get('reporting_period_end'),
            documentation_urls=request.data.get('documentation_urls', []),
            initial_estimate_credits=request.data.get('initial_estimate_credits'),
        )
        mrv_request.save()
        
        project.status = 'SUBMITTED_FOR_MRV'
        project.submitted_at = datetime.utcnow()
        project.save()
        
        return Response(
            {'message': 'Project submitted for MRV', 'mrv_request_id': str(mrv_request.id)},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def mrv_status(self, request, pk=None):
        """Get MRV status for project"""
        project = Project.objects.get(id=pk)
        try:
            mrv_request = MRVRequest.objects.get(project=project)
            return Response({
                'status': mrv_request.status,
                'submitted_at': mrv_request.submitted_at,
                'updated_at': mrv_request.updated_at,
            })
        except MRVRequest.DoesNotExist:
            return Response(
                {'message': 'No MRV request found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProjectMethodologyViewSet(viewsets.ModelViewSet):
    """ViewSet for project methodologies"""
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectMethodologySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'standard']
    
    def get_queryset(self):
        return ProjectMethodology.objects()
    
    def perform_create(self, serializer):
        """Create project methodology"""
        project_id = self.request.data.get('project_id')
        project = Project.objects.get(id=project_id)
        
        methodology = ProjectMethodology(
            project=project,
            methodology_code=serializer.validated_data['methodology_code'],
            standard=serializer.validated_data['standard'],
            description=serializer.validated_data.get('description'),
            documentation_url=serializer.validated_data.get('documentation_url'),
            parameters=serializer.validated_data.get('parameters', {}),
        )
        methodology.save()
        
        project.has_methodology = True
        project.save()
