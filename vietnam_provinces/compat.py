from typing import TypeVar


# Type variable for enum classes
EnumType = TypeVar('EnumType')

try:
    from enum_tools.documentation import document_enum
except ModuleNotFoundError:

    def document_enum(an_enum: EnumType) -> EnumType:
        """No-op fallback when enum_tools is not installed."""
        return an_enum


__all__ = ['document_enum']
