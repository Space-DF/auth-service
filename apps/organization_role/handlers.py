from common.apps.organization.handler import NewOrganizationHandlerBase
from common.apps.organization_user.models import OrganizationUser
from django.db import transaction
from django_tenants.utils import get_tenant_model, tenant_context


class NewOrganizationHandler(NewOrganizationHandlerBase):
    @transaction.atomic
    def handle(self):
        organization = get_tenant_model().objects.get(
            schema_name=self._organization.slug_name
        )
        with tenant_context(organization):
            # Create owner user
            owner = OrganizationUser(email=self._owner_email, is_owner=True)
            owner.save()
