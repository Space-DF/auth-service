from common.apps.billing.mixins import BaseQuota


class SpaceQuota(BaseQuota):
    release_actions = {"destroy"}
    rules = {
        "create": "space.max_count",
        "destroy": "space.max_count",
    }
