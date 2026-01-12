import re

TOPIC_NONSPACE_REGEX = re.compile(
    r"^tenant/(?P<org>[a-z0-9\-]+)/device/(?P<device>[^/]+)(?:/.*)?$",
    re.IGNORECASE,
)

TOPIC_SPACE_REGEX = re.compile(
    r"^tenant/(?P<org>[a-z0-9\-]+)/space/(?P<space>[a-z0-9\-]+)/device/(?P<device>[^/]+)(?:/.*)?$",
    re.IGNORECASE,
)

TOPIC_ENTITY_SPACE_REGEX = re.compile(
    r"^tenant/(?P<org>[a-z0-9\-]+)/space/(?P<space>[a-z0-9\-]+)/entity/(?P<entity>[^/]+)(?:/.*)?$",
    re.IGNORECASE,
)

TOPIC_ENTITY_NONSPACE_REGEX = re.compile(
    r"^tenant/(?P<org>[a-z0-9\-]+)/entity/(?P<entity>[^/]+)(?:/.*)?$",
    re.IGNORECASE,
)
