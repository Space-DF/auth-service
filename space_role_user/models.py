from authentication.models import OrganizationUser
from common.models.base_model import BaseModel
from django.db import models
from space_role.models import SpaceRole


class SpaceRoleUser(BaseModel):
    space_role = models.ForeignKey(
        SpaceRole,
        related_name="space_role_user",
        on_delete=models.CASCADE,
    )
    organization_user = models.ForeignKey(
        OrganizationUser, related_name="space_role_user", on_delete=models.CASCADE
    )
