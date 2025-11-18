"""DRF permissions for Djvurn Rbac."""


# TODO: Create your custom permissions following this pattern:
# class IsOwnerOrReadOnly(permissions.BasePermission):
#     """
#     Object-level permission to only allow owners to edit.
#
#     Safe methods (GET, HEAD, OPTIONS) are allowed for any authenticated user.
#     Write methods (POST, PUT, PATCH, DELETE) are only allowed for the owner.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         """
#         Check if user has permission for the object.
#
#         Args:
#             request: The HTTP request
#             view: The view being accessed
#             obj: The object being accessed
#
#         Returns:
#             bool: True if user has permission, False otherwise
#         """
#         # Read permissions for any authenticated user
#         if request.method in permissions.SAFE_METHODS:
#             return True
#
#         # Write permissions only for owner
#         return obj.owner == request.user


# class IsTeamAdminOrReadOnly(permissions.BasePermission):
#     """
#     Object-level permission for team-based resources.
#
#     Safe methods are allowed for team members.
#     Write methods are only allowed for team admins.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         """Check if user has permission based on team role."""
#         # Read permissions for team members
#         if request.method in permissions.SAFE_METHODS:
#             return obj.team.is_member(request.user)
#
#         # Write permissions only for team admins
#         return obj.team.is_admin(request.user)
