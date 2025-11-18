"""DRF ViewSets for djvurn-rbac."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm, get_perms, remove_perm
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

User = get_user_model()


class PermissionViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing object-level permissions.

    Provides endpoints for:
    - Checking if a user has a permission on an object
    - Assigning permissions to users (coming soon)
    - Removing permissions from users (coming soon)
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="check")
    def check(self, request: Request) -> Response:
        """
        Check if a user has a specific permission on an object.

        Query Parameters:
            user_id (int): ID of the user to check
            permission (str): Permission code (e.g., 'auth.view_user')
            content_type (str): Content type in 'app.model' format
            object_id (int): ID of the object

        Returns:
            Response: JSON with 'has_permission' boolean

        Example:
            GET /api/permissions/check/?user_id=1&permission=auth.view_user&content_type=auth.user&object_id=2

            Response 200:
            {
                "has_permission": true
            }
        """
        # Validate required parameters
        user_id: str | None = request.query_params.get("user_id")
        permission: str | None = request.query_params.get("permission")
        content_type_str: str | None = request.query_params.get("content_type")
        object_id: str | None = request.query_params.get("object_id")

        if not all([user_id, permission, content_type_str, object_id]):
            return Response(
                {
                    "error": "Missing required parameters",
                    "required": ["user_id", "permission", "content_type", "object_id"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the user
            user: User = User.objects.get(id=int(user_id))

            # Parse content type (format: "app.model")
            app_label, model = content_type_str.split(".")
            content_type: ContentType = ContentType.objects.get(app_label=app_label, model=model)

            # Get the object
            model_class = content_type.model_class()
            if model_class is None:
                return Response(
                    {"error": f"Invalid content type: {content_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj: Any = model_class.objects.get(id=int(object_id))

            # Check permission using django-guardian (extends user.has_perm to support objects)
            has_permission: bool = user.has_perm(permission, obj)

            return Response({"has_permission": has_permission}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content type: {content_type_str}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": f"Invalid parameter format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"], url_path="assign")
    def assign(self, request: Request) -> Response:
        """
        Assign a permission to a user for an object.

        Request Body:
            user_id (int): ID of the user to assign permission to
            permission (str): Permission code (e.g., 'auth.change_user')
            content_type (str): Content type in 'app.model' format
            object_id (int): ID of the object

        Returns:
            Response: JSON with 'success' boolean

        Example:
            POST /api/permissions/assign/
            {
                "user_id": 1,
                "permission": "auth.change_user",
                "content_type": "auth.user",
                "object_id": 2
            }

            Response 201:
            {
                "success": true,
                "message": "Permission assigned successfully"
            }
        """
        # Validate required parameters
        user_id: str | None = request.data.get("user_id")
        permission: str | None = request.data.get("permission")
        content_type_str: str | None = request.data.get("content_type")
        object_id: str | None = request.data.get("object_id")

        if not all([user_id, permission, content_type_str, object_id]):
            return Response(
                {
                    "error": "Missing required parameters",
                    "required": ["user_id", "permission", "content_type", "object_id"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the user
            user: User = User.objects.get(id=int(user_id))

            # Parse content type (format: "app.model")
            app_label, model = content_type_str.split(".")
            content_type: ContentType = ContentType.objects.get(app_label=app_label, model=model)

            # Get the object
            model_class = content_type.model_class()
            if model_class is None:
                return Response(
                    {"error": f"Invalid content type: {content_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj: Any = model_class.objects.get(id=int(object_id))

            # Validate permission exists
            try:
                Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=permission.split(".")[-1],  # Extract codename from 'app.perm'
                )
            except Permission.DoesNotExist:
                return Response(
                    {"error": f"Invalid permission: {permission}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Assign permission using django-guardian
            assign_perm(permission, user, obj)

            return Response(
                {"success": True, "message": "Permission assigned successfully"},
                status=status.HTTP_201_CREATED,
            )

        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content type: {content_type_str}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": f"Invalid parameter format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"], url_path="remove")
    def remove(self, request: Request) -> Response:
        """
        Remove a permission from a user for an object.

        Request Body:
            user_id (int): ID of the user to remove permission from
            permission (str): Permission code (e.g., 'auth.delete_user')
            content_type (str): Content type in 'app.model' format
            object_id (int): ID of the object

        Returns:
            Response: JSON with 'success' boolean

        Example:
            POST /api/permissions/remove/
            {
                "user_id": 1,
                "permission": "auth.delete_user",
                "content_type": "auth.user",
                "object_id": 2
            }

            Response 200:
            {
                "success": true,
                "message": "Permission removed successfully"
            }
        """
        # Validate required parameters
        user_id: str | None = request.data.get("user_id")
        permission: str | None = request.data.get("permission")
        content_type_str: str | None = request.data.get("content_type")
        object_id: str | None = request.data.get("object_id")

        if not all([user_id, permission, content_type_str, object_id]):
            return Response(
                {
                    "error": "Missing required parameters",
                    "required": ["user_id", "permission", "content_type", "object_id"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the user
            user: User = User.objects.get(id=int(user_id))

            # Parse content type (format: "app.model")
            app_label, model = content_type_str.split(".")
            content_type: ContentType = ContentType.objects.get(app_label=app_label, model=model)

            # Get the object
            model_class = content_type.model_class()
            if model_class is None:
                return Response(
                    {"error": f"Invalid content type: {content_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj: Any = model_class.objects.get(id=int(object_id))

            # Validate permission exists
            try:
                Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=permission.split(".")[-1],  # Extract codename from 'app.perm'
                )
            except Permission.DoesNotExist:
                return Response(
                    {"error": f"Invalid permission: {permission}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Remove permission using django-guardian (idempotent - won't error if not assigned)
            remove_perm(permission, user, obj)

            return Response(
                {"success": True, "message": "Permission removed successfully"},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content type: {content_type_str}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": f"Invalid parameter format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], url_path="list")
    def list_permissions(self, request: Request) -> Response:
        """
        List all permissions a user has on an object.

        Query Parameters:
            user_id (int): ID of the user
            content_type (str): Content type in 'app.model' format
            object_id (int): ID of the object

        Returns:
            Response: JSON with list of permission codes

        Example:
            GET /api/permissions/list/?user_id=1&content_type=auth.user&object_id=2

            Response 200:
            {
                "permissions": ["auth.view_user", "auth.change_user"]
            }
        """
        # Validate required parameters
        user_id: str | None = request.query_params.get("user_id")
        content_type_str: str | None = request.query_params.get("content_type")
        object_id: str | None = request.query_params.get("object_id")

        if not all([user_id, content_type_str, object_id]):
            return Response(
                {
                    "error": "Missing required parameters",
                    "required": ["user_id", "content_type", "object_id"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the user
            user: User = User.objects.get(id=int(user_id))

            # Parse content type (format: "app.model")
            app_label, model = content_type_str.split(".")
            content_type: ContentType = ContentType.objects.get(app_label=app_label, model=model)

            # Get the object
            model_class = content_type.model_class()
            if model_class is None:
                return Response(
                    {"error": f"Invalid content type: {content_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj: Any = model_class.objects.get(id=int(object_id))

            # Get all permissions using django-guardian
            perms: list[str] = get_perms(user, obj)

            # Convert codenames to full permission strings (e.g., "view_user" -> "auth.view_user")
            full_perms: list[str] = [f"{app_label}.{perm}" for perm in perms]

            return Response({"permissions": full_perms}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content type: {content_type_str}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": f"Invalid parameter format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"], url_path="bulk-assign")
    def bulk_assign(self, request: Request) -> Response:
        """
        Assign multiple permissions to a user for an object.

        Request Body:
            user_id (int): ID of the user
            permissions (list[str]): List of permission codes
            content_type (str): Content type in 'app.model' format
            object_id (int): ID of the object

        Returns:
            Response: JSON with success status, assigned count, and skipped permissions

        Example:
            POST /api/permissions/bulk-assign/
            {
                "user_id": 1,
                "permissions": ["auth.view_user", "auth.change_user"],
                "content_type": "auth.user",
                "object_id": 2
            }

            Response 201:
            {
                "success": true,
                "assigned_count": 2,
                "skipped": []
            }
        """
        # Validate required parameters
        user_id: str | None = request.data.get("user_id")
        permissions: list[str] | None = request.data.get("permissions")
        content_type_str: str | None = request.data.get("content_type")
        object_id: str | None = request.data.get("object_id")

        if not all([user_id is not None, permissions is not None, content_type_str, object_id]):
            return Response(
                {
                    "error": "Missing required parameters",
                    "required": ["user_id", "permissions", "content_type", "object_id"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(permissions, list):
            return Response(
                {"error": "permissions must be a list"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the user
            user: User = User.objects.get(id=int(user_id))

            # Parse content type (format: "app.model")
            app_label, model = content_type_str.split(".")
            content_type: ContentType = ContentType.objects.get(app_label=app_label, model=model)

            # Get the object
            model_class = content_type.model_class()
            if model_class is None:
                return Response(
                    {"error": f"Invalid content type: {content_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj: Any = model_class.objects.get(id=int(object_id))

            # Process each permission
            assigned_count: int = 0
            skipped: list[str] = []

            for permission in permissions:
                # Validate permission exists
                try:
                    Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=permission.split(".")[-1],
                    )
                    # Assign if valid
                    assign_perm(permission, user, obj)
                    assigned_count += 1
                except Permission.DoesNotExist:
                    skipped.append(permission)

            return Response(
                {
                    "success": True,
                    "assigned_count": assigned_count,
                    "skipped": skipped,
                },
                status=status.HTTP_201_CREATED,
            )

        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content type: {content_type_str}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": f"Invalid parameter format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"], url_path="bulk-remove")
    def bulk_remove(self, request: Request) -> Response:
        """
        Remove multiple permissions from a user for an object.

        Request Body:
            user_id (int): ID of the user
            permissions (list[str]): List of permission codes
            content_type (str): Content type in 'app.model' format
            object_id (int): ID of the object

        Returns:
            Response: JSON with success status, removed count, and skipped permissions

        Example:
            POST /api/permissions/bulk-remove/
            {
                "user_id": 1,
                "permissions": ["auth.view_user", "auth.change_user"],
                "content_type": "auth.user",
                "object_id": 2
            }

            Response 200:
            {
                "success": true,
                "removed_count": 2,
                "skipped": []
            }
        """
        # Validate required parameters
        user_id: str | None = request.data.get("user_id")
        permissions: list[str] | None = request.data.get("permissions")
        content_type_str: str | None = request.data.get("content_type")
        object_id: str | None = request.data.get("object_id")

        if not all([user_id is not None, permissions is not None, content_type_str, object_id]):
            return Response(
                {
                    "error": "Missing required parameters",
                    "required": ["user_id", "permissions", "content_type", "object_id"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(permissions, list):
            return Response(
                {"error": "permissions must be a list"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the user
            user: User = User.objects.get(id=int(user_id))

            # Parse content type (format: "app.model")
            app_label, model = content_type_str.split(".")
            content_type: ContentType = ContentType.objects.get(app_label=app_label, model=model)

            # Get the object
            model_class = content_type.model_class()
            if model_class is None:
                return Response(
                    {"error": f"Invalid content type: {content_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            obj: Any = model_class.objects.get(id=int(object_id))

            # Process each permission
            removed_count: int = 0
            skipped: list[str] = []

            for permission in permissions:
                # Validate permission exists
                try:
                    Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=permission.split(".")[-1],
                    )
                    # Remove if valid (idempotent - safe even if not assigned)
                    remove_perm(permission, user, obj)
                    removed_count += 1
                except Permission.DoesNotExist:
                    skipped.append(permission)

            return Response(
                {
                    "success": True,
                    "removed_count": removed_count,
                    "skipped": skipped,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Invalid content type: {content_type_str}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, AttributeError) as e:
            return Response(
                {"error": f"Invalid parameter format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )
