"""Substitution Links client for Open Dental SDK."""

from typing import List, Optional, Union
from ...base.resource import BaseResource
from .models import (
    SubstitutionLink,
    CreateSubstitutionLinkRequest,
    UpdateSubstitutionLinkRequest,
    SubstitutionLinkListResponse,
    SubstitutionLinkSearchRequest
)


class SubstitutionLinksClient(BaseResource):
    """
    Client for managing insurance procedure code substitutions/downgrades.
    
    Substitution links define when insurance companies substitute one procedure 
    code for another (typically a less expensive alternative). Also known as 
    "downgrades" in dental insurance.
    """
    
    def __init__(self, client):
        """Initialize the substitution links client."""
        super().__init__(client, "substitutionlinks")
    
    def get(self, subst_num: Union[int, str]) -> SubstitutionLink:
        """
        Get a substitution link by ID.
        
        Args:
            subst_num: Substitution link number
            
        Returns:
            SubstitutionLink object
        """
        subst_num = self._validate_id(subst_num)
        endpoint = self._build_endpoint(subst_num)
        response = self._get(endpoint)
        return self._handle_response(response, SubstitutionLink)
    
    def list(self, page: int = 1, per_page: int = 50) -> SubstitutionLinkListResponse:
        """
        List all substitution links.
        
        Args:
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            SubstitutionLinkListResponse with list of substitution links
        """
        params = {"page": page, "per_page": per_page}
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return SubstitutionLinkListResponse(**response)
        elif isinstance(response, list):
            return SubstitutionLinkListResponse(
                substitution_links=[SubstitutionLink(**item) for item in response],
                total=len(response), page=page, per_page=per_page
            )
        return SubstitutionLinkListResponse(substitution_links=[], total=0, page=page, per_page=per_page)
    
    def create(self, request: CreateSubstitutionLinkRequest) -> SubstitutionLink:
        """
        Create a new substitution link (downgrade rule).
        
        Args:
            request: CreateSubstitutionLinkRequest with procedure codes and conditions
            
        Returns:
            Created SubstitutionLink object
            
        Example:
            >>> # Create a downgrade rule: white filling -> amalgam filling
            >>> request = CreateSubstitutionLinkRequest(
            ...     proc_code_num=1234,  # White filling code
            ...     substitute_code_num=5678,  # Amalgam filling code
            ...     substitute_only_if="Posterior",
            ...     plan_num=0  # Applies to all plans
            ... )
            >>> link = client.substitution_links.create(request)
        """
        endpoint = self._build_endpoint()
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, SubstitutionLink)
    
    def update(self, subst_num: Union[int, str], request: UpdateSubstitutionLinkRequest) -> SubstitutionLink:
        """
        Update an existing substitution link.
        
        Args:
            subst_num: Substitution link number
            request: UpdateSubstitutionLinkRequest with fields to update
            
        Returns:
            Updated SubstitutionLink object
        """
        subst_num = self._validate_id(subst_num)
        endpoint = self._build_endpoint(subst_num)
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, SubstitutionLink)
    
    def delete(self, subst_num: Union[int, str]) -> bool:
        """
        Delete a substitution link.
        
        Args:
            subst_num: Substitution link number
            
        Returns:
            True if successful
        """
        subst_num = self._validate_id(subst_num)
        endpoint = self._build_endpoint(subst_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def search(self, search_params: SubstitutionLinkSearchRequest) -> SubstitutionLinkListResponse:
        """
        Search for substitution links by procedure codes or plan.
        
        Args:
            search_params: SubstitutionLinkSearchRequest with search criteria
            
        Returns:
            SubstitutionLinkListResponse with matching substitution links
        """
        endpoint = self._build_endpoint("search")
        params = search_params.model_dump(by_alias=True, exclude_none=True)
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return SubstitutionLinkListResponse(**response)
        elif isinstance(response, list):
            return SubstitutionLinkListResponse(
                substitution_links=[SubstitutionLink(**item) for item in response],
                total=len(response), page=search_params.page, per_page=search_params.per_page
            )
        return SubstitutionLinkListResponse(
            substitution_links=[], total=0, page=search_params.page, per_page=search_params.per_page
        )
    
    def get_by_procedure_code(self, proc_code_num: int) -> List[SubstitutionLink]:
        """
        Get all substitution links for a specific procedure code.
        
        Args:
            proc_code_num: Procedure code number
            
        Returns:
            List of SubstitutionLink objects
        """
        search_params = SubstitutionLinkSearchRequest(proc_code_num=proc_code_num, per_page=1000)
        result = self.search(search_params)
        return result.substitution_links
    
    def get_by_plan(self, plan_num: int) -> List[SubstitutionLink]:
        """
        Get all substitution links for a specific insurance plan.
        
        Args:
            plan_num: Insurance plan number
            
        Returns:
            List of SubstitutionLink objects
        """
        search_params = SubstitutionLinkSearchRequest(plan_num=plan_num, per_page=1000)
        result = self.search(search_params)
        return result.substitution_links

