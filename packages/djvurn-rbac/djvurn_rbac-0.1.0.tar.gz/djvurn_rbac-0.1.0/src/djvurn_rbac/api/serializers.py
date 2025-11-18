"""DRF serializers for Djvurn Rbac."""


# TODO: Import your models
# from ..models import Example


# TODO: Create your serializers following this pattern:
# class ExampleSerializer(serializers.ModelSerializer):
#     """Serializer for Example model."""
#
#     # Add custom fields if needed
#     custom_field = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Example
#         fields = [
#             'id',
#             'name',
#             'description',
#             'custom_field',
#             'created_at',
#             'updated_at',
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']
#
#     def get_custom_field(self, obj):
#         """Get custom field value."""
#         return obj.calculate_something()
#
#     def validate_name(self, value):
#         """Validate name field."""
#         if not value:
#             raise serializers.ValidationError("Name cannot be empty")
#         return value
