from django.db import models


class SpaceRoleType(models.TextChoices):
    ADMIN_ROLE = "Admin"
    EDITOR_ROLE = "Editor"
    VIEWER_ROLE = "Viewer"
