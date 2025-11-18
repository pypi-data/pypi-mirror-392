"""DRF API module for Djvurn Rbac."""

from rest_framework.routers import DefaultRouter

from .views import PermissionViewSet

# Create router
router = DefaultRouter()

# Register ViewSets
router.register(r"permissions", PermissionViewSet, basename="permission")

__all__ = ["router"]
