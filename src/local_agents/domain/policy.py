from enum import StrEnum


class PrivacyLevel(StrEnum):
    LOCAL_ONLY = "local_only"
    ONLINE_ALLOWED = "online_allowed"
    REQUIRES_APPROVAL = "requires_approval"


class AgentIntent(StrEnum):
    STUDY = "study"
    MAIL = "mail"
    ADMIN = "admin"
    GENERAL = "general"
