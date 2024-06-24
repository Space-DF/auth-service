from common.models.base_model import BaseModel
from django.contrib.postgres.fields import ArrayField
from django.db import models
from space.models import Space
from space_role.constants import Permission


class Policy(BaseModel):
    name = models.CharField(max_length=256)
    description = models.TextField()
    tags = ArrayField(models.CharField(max_length=256))
    permissions = ArrayField(
        models.CharField(max_length=256, choices=Permission.choices)
    )


class SpaceRole(BaseModel):
    name = models.CharField(max_length=256)
    space = models.ForeignKey(
        Space, related_name="space_role", on_delete=models.CASCADE
    )
    policies = models.ManyToManyField(Policy)
