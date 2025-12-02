"""
Projects app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.projects.views import ProjectViewSet, CarbonCategoryViewSet, ProjectMethodologyViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'categories', CarbonCategoryViewSet, basename='carbon-category')
router.register(r'methodologies', ProjectMethodologyViewSet, basename='methodology')

urlpatterns = router.urls
