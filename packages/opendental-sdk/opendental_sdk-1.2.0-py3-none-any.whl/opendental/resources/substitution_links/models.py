"""Substitution Links models for Open Dental SDK."""

from datetime import datetime
from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class SubstitutionLink(BaseModel):
    """
    Substitution Link model.
    
    Represents insurance procedure code substitutions/downgrades.
    When an insurance company substitutes one procedure code for another 
    (typically a less expensive alternative).
    """
    
    # Primary identifier
    id: int = Field(..., alias="SubstNum", description="Substitution link number (primary key)")
    
    # Procedure codes
    proc_code_num: Optional[int] = Field(None, alias="ProcCodeNum", description="Original procedure code number")
    substitute_code_num: Optional[int] = Field(None, alias="SubstituteCodeNum", description="Substitute/downgrade procedure code number")
    
    # Conditions
    substitute_only_if: Optional[str] = Field(None, alias="SubstituteOnlyIf", description="Conditions for substitution")
    
    # Metadata
    plan_num: Optional[int] = Field(None, alias="PlanNum", description="Insurance plan number (0 if applies to all plans)")
    
    # Timestamps
    date_created: Optional[datetime] = Field(None, alias="DateCreated", description="Date link was created")
    date_modified: Optional[datetime] = Field(None, alias="DateTStamp", description="Date link was last modified")


class CreateSubstitutionLinkRequest(BaseModel):
    """Request model for creating a new substitution link."""
    
    # Required fields
    proc_code_num: int = Field(..., alias="ProcCodeNum", description="Original procedure code number")
    substitute_code_num: int = Field(..., alias="SubstituteCodeNum", description="Substitute procedure code number")
    
    # Optional fields
    substitute_only_if: Optional[str] = Field(None, alias="SubstituteOnlyIf", description="Conditions for substitution")
    plan_num: Optional[int] = Field(0, alias="PlanNum", description="Insurance plan number (0 for all plans)")


class UpdateSubstitutionLinkRequest(BaseModel):
    """Request model for updating an existing substitution link."""
    
    # All fields are optional for updates
    proc_code_num: Optional[int] = Field(None, alias="ProcCodeNum", description="Original procedure code number")
    substitute_code_num: Optional[int] = Field(None, alias="SubstituteCodeNum", description="Substitute procedure code number")
    substitute_only_if: Optional[str] = Field(None, alias="SubstituteOnlyIf", description="Conditions for substitution")
    plan_num: Optional[int] = Field(None, alias="PlanNum", description="Insurance plan number")


class SubstitutionLinkListResponse(BaseModel):
    """Response model for substitution link list operations."""
    
    substitution_links: List[SubstitutionLink]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None


class SubstitutionLinkSearchRequest(BaseModel):
    """Request model for searching substitution links."""
    
    proc_code_num: Optional[int] = Field(None, alias="ProcCodeNum", description="Original procedure code number")
    substitute_code_num: Optional[int] = Field(None, alias="SubstituteCodeNum", description="Substitute procedure code number")
    plan_num: Optional[int] = Field(None, alias="PlanNum", description="Insurance plan number")
    
    # Pagination
    page: Optional[int] = 1
    per_page: Optional[int] = 50

