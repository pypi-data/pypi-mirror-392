"""Django models for Djvurn Rbac."""

from django.contrib.auth import get_user_model

User = get_user_model()


# TODO: Add any model extensions or new models here
# This package wraps django-guardian, so most models come from there.
# Only add models here if you need to extend functionality.

# Example of extending a model from the base package:
# from django_guardian.models import BaseModel
#
# class ExtendedModel(models.Model):
#     """Extended model adding team support."""
#
#     base_model = models.OneToOneField(
#         BaseModel,
#         on_delete=models.CASCADE,
#         related_name='extension'
#     )
#     team = models.ForeignKey(
#         'Team',  # If using djvurn-rbac
#         on_delete=models.CASCADE,
#         related_name='extended_models'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'Extended Model'
#         verbose_name_plural = 'Extended Models'
#
#     def __str__(self):
#         return f"{self.base_model} (Team: {self.team})"
