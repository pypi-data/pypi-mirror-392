"""Substitution Links types and enums for Open Dental SDK."""

from enum import Enum


class SubstitutionCondition(str, Enum):
    """Common substitution conditions."""
    ALWAYS = "Always"
    NEVER = "Never"
    POSTERIOR = "Posterior"  # Back teeth only
    ANTERIOR = "Anterior"  # Front teeth only
    IF_NO_BENEFIT = "IfNoBenefit"  # If no benefit for original procedure
    SPECIFIC_TOOTH = "SpecificTooth"  # For specific tooth numbers

