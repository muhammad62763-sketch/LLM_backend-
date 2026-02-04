from enum import Enum

class MessageRoleType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Rate Limiting
DEFAULT_RPM = 30
DEFAULT_TPM = 10000
DEFAULT_TPD = 500000

# API Timeouts
API_REQUEST_TIMEOUT = 60.0

# Token Estimation
CHARS_PER_TOKEN = 4
