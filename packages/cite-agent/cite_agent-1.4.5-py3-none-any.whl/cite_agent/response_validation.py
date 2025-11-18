#!/usr/bin/env python3
"""
Response Validation Utilities

Safe attribute access and validation for backend API responses.
Prevents crashes from malformed or incomplete responses.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validating a response"""
    valid: bool
    value: Any
    errors: List[str]


def safe_get(data: Any, *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values with fallback.

    Examples:
        safe_get(paper, 'title', default='Unknown')
        safe_get(response, 'data', 'papers', 0, 'doi', default='')
    """
    try:
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
                if result is default:
                    return default
            elif isinstance(result, (list, tuple)) and isinstance(key, int):
                if 0 <= key < len(result):
                    result = result[key]
                else:
                    return default
            else:
                return default
        return result
    except (TypeError, AttributeError, KeyError, IndexError):
        return default


def safe_list(data: Any, key: str = None, default: List = None) -> List:
    """
    Safely extract a list from response data.

    Examples:
        safe_list(response, 'papers', default=[])
        safe_list(data)  # Returns data if it's a list, else []
    """
    if default is None:
        default = []

    try:
        if key:
            value = data.get(key, default) if isinstance(data, dict) else default
        else:
            value = data

        if isinstance(value, list):
            return value
        elif isinstance(value, (tuple, set)):
            return list(value)
        else:
            return default
    except (TypeError, AttributeError):
        return default


def safe_str(data: Any, key: str = None, default: str = "") -> str:
    """
    Safely extract a string value.

    Examples:
        safe_str(paper, 'title', default='Untitled')
        safe_str(response.get('error'))
    """
    try:
        if key:
            value = data.get(key, default) if isinstance(data, dict) else default
        else:
            value = data

        if value is None:
            return default
        return str(value)
    except (TypeError, AttributeError):
        return default


def safe_int(data: Any, key: str = None, default: int = 0) -> int:
    """
    Safely extract an integer value.

    Examples:
        safe_int(paper, 'year', default=0)
        safe_int(response, 'count')
    """
    try:
        if key:
            value = data.get(key, default) if isinstance(data, dict) else default
        else:
            value = data

        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError, AttributeError):
        return default


def safe_float(data: Any, key: str = None, default: float = 0.0) -> float:
    """
    Safely extract a float value.

    Examples:
        safe_float(metrics, 'score', default=0.0)
    """
    try:
        if key:
            value = data.get(key, default) if isinstance(data, dict) else default
        else:
            value = data

        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError, AttributeError):
        return default


def safe_bool(data: Any, key: str = None, default: bool = False) -> bool:
    """
    Safely extract a boolean value.

    Examples:
        safe_bool(response, 'success', default=False)
    """
    try:
        if key:
            value = data.get(key, default) if isinstance(data, dict) else default
        else:
            value = data

        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    except (TypeError, AttributeError):
        return default


def validate_paper_response(paper_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a paper response from Archive API.
    Ensures required fields are present and provides safe defaults.
    """
    errors = []

    # Required fields with safe defaults
    validated = {
        'title': safe_str(paper_data, 'title', default='Unknown Title'),
        'authors': safe_list(paper_data, 'authors', default=['Unknown Author']),
        'year': safe_int(paper_data, 'year', default=0),
        'doi': safe_str(paper_data, 'doi', default=''),
        'abstract': safe_str(paper_data, 'abstract', default=''),
        'source': safe_str(paper_data, 'source', default='unknown'),
        'url': safe_str(paper_data, 'url', default=''),
        'citation_count': safe_int(paper_data, 'citation_count', default=0),
    }

    # Check for critical missing fields
    if validated['title'] == 'Unknown Title' and 'title' not in paper_data:
        errors.append("Missing required field: title")

    if validated['authors'] == ['Unknown Author'] and 'authors' not in paper_data:
        errors.append("Missing required field: authors")

    if validated['year'] == 0:
        # Try alternative field names
        validated['year'] = safe_int(paper_data, 'publication_year', default=0)
        if validated['year'] == 0:
            validated['year'] = safe_int(paper_data, 'pub_year', default=0)

    # Handle DOI from alternative locations
    if not validated['doi']:
        validated['doi'] = safe_get(paper_data, 'identifiers', 'doi', default='')

    return ValidationResult(
        valid=len(errors) == 0,
        value=validated,
        errors=errors
    )


def validate_finance_response(finance_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a financial data response from FinSight API.
    """
    errors = []

    validated = {
        'ticker': safe_str(finance_data, 'ticker', default=''),
        'company_name': safe_str(finance_data, 'company_name', default='Unknown Company'),
        'data': safe_get(finance_data, 'data', default={}),
        'timestamp': safe_str(finance_data, 'timestamp', default=''),
        'source': safe_str(finance_data, 'source', default='unknown'),
    }

    if not validated['ticker']:
        errors.append("Missing required field: ticker")

    if not validated['data']:
        errors.append("Missing or empty data field")

    return ValidationResult(
        valid=len(errors) == 0,
        value=validated,
        errors=errors
    )


def validate_search_response(search_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a search results response.
    """
    errors = []

    # Handle both array and object responses
    if isinstance(search_data, list):
        papers = search_data
    else:
        papers = safe_list(search_data, 'papers', default=[])
        if not papers:
            papers = safe_list(search_data, 'results', default=[])

    validated_papers = []
    for i, paper in enumerate(papers):
        paper_result = validate_paper_response(paper)
        if not paper_result.valid:
            errors.append(f"Paper {i}: {', '.join(paper_result.errors)}")
        validated_papers.append(paper_result.value)

    validated = {
        'papers': validated_papers,
        'total': safe_int(search_data, 'total', default=len(validated_papers)),
        'query': safe_str(search_data, 'query', default=''),
    }

    return ValidationResult(
        valid=len(errors) == 0,
        value=validated,
        errors=errors
    )


def safe_response_extract(response_data: Any, expected_type: str = 'dict') -> Any:
    """
    Safely extract response data with type checking.

    Args:
        response_data: Raw response from API
        expected_type: 'dict', 'list', 'str', 'int', 'float'

    Returns:
        Properly typed data or safe default
    """
    defaults = {
        'dict': {},
        'list': [],
        'str': '',
        'int': 0,
        'float': 0.0,
        'bool': False,
    }

    default = defaults.get(expected_type, None)

    if response_data is None:
        return default

    if expected_type == 'dict' and isinstance(response_data, dict):
        return response_data
    elif expected_type == 'list' and isinstance(response_data, list):
        return response_data
    elif expected_type == 'str':
        return safe_str(response_data)
    elif expected_type == 'int':
        return safe_int(response_data)
    elif expected_type == 'float':
        return safe_float(response_data)
    elif expected_type == 'bool':
        return safe_bool(response_data)

    return default


# Convenience function for error handling in API calls
def handle_api_error(response: Any, default_message: str = "API request failed") -> str:
    """
    Extract error message from various response formats.
    """
    if isinstance(response, dict):
        # Try common error field names
        for field in ['error', 'message', 'detail', 'error_message', 'msg']:
            if field in response:
                return safe_str(response, field, default=default_message)

    if isinstance(response, str):
        return response

    return default_message
