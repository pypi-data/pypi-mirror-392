from enum import Enum


class RoleEnum(str, Enum):
    full_access = "full_access"
    standard = "standard"
    sudo = "sudo"