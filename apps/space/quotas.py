from common.apps.billing.constants import FeatureCode, FeatureUsageScope
from common.apps.billing.mixins import BaseQuota


class SpaceQuota(BaseQuota):
    reserve_actions = {"create"}
    release_actions = {"destroy"}
    rules = {
        "create": {
            "feature": FeatureCode.SPACE_MAX_COUNT,
            "scope": FeatureUsageScope.USER,
        },
        "destroy": {
            "feature": FeatureCode.SPACE_MAX_COUNT,
            "scope": FeatureUsageScope.USER,
        },
    }
