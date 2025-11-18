"""
License filtering and validation for Rust crates.

Provides license detection, validation, and filtering based on allow/deny lists.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

# Common disallowed license patterns (case-insensitive)
DISALLOWED_LICENSE_SUBSTRINGS = [
    "agpl",
    "gpl-3.0",
    "gpl3",
    "gpl v3",
    "gplv3",
    "copyleft",
]

# Common allowed licenses (SPDX identifiers)
ALLOWED_LICENSE_PATTERNS = [
    r"^(MIT|Apache-2\.0|BSD-[23]-Clause|ISC|Unlicense|0BSD)$",
    r"^(MIT|Apache-2\.0|BSD-[23]-Clause|ISC|Unlicense|0BSD)\s*OR\s*(MIT|Apache-2\.0|BSD-[23]-Clause|ISC|Unlicense|0BSD)$",
    r"^(MIT|Apache-2\.0|BSD-[23]-Clause|ISC|Unlicense|0BSD)\s*AND\s*(MIT|Apache-2\.0|BSD-[23]-Clause|ISC|Unlicense|0BSD)$",
]


@dataclass
class LicenseCheckResult:
    """Result of license checking for a crate."""
    
    detected_licenses: List[str]
    status: str  # "allowed", "forbidden", "unknown", "warning"
    message: str
    confidence: float = 0.0  # 0.0 to 1.0
    
    def is_allowed(self) -> bool:
        """Check if the license is allowed."""
        return self.status == "allowed"
    
    def is_forbidden(self) -> bool:
        """Check if the license is forbidden."""
        return self.status == "forbidden"
    
    def requires_review(self) -> bool:
        """Check if the license requires manual review."""
        return self.status in ("unknown", "warning")


class LicenseFilter:
    """License detection and filtering for Rust crates."""
    
    def __init__(
        self,
        allowed_licenses: Optional[List[str]] = None,
        denied_licenses: Optional[List[str]] = None,
        require_explicit_allow: bool = False,
    ):
        """
        Initialize license filter.
        
        Args:
            allowed_licenses: List of allowed license SPDX identifiers (None = use defaults)
            denied_licenses: List of denied license SPDX identifiers (None = use defaults)
            require_explicit_allow: If True, only explicitly allowed licenses pass
        """
        self.allowed_licenses: Set[str] = set(
            [lic.lower() for lic in (allowed_licenses or [])]
        )
        self.denied_licenses: Set[str] = set(
            [lic.lower() if isinstance(lic, str) else str(lic).lower() for lic in (denied_licenses or DISALLOWED_LICENSE_SUBSTRINGS)]
        )
        self.require_explicit_allow = require_explicit_allow
        
        # Build regex patterns for allowed licenses
        self.allowed_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in ALLOWED_LICENSE_PATTERNS
        ]
    
    def _split_license_expression(self, license_expr: str) -> List[str]:
        """Split SPDX license expression into individual licenses."""
        if not license_expr:
            return []
        
        # Handle SPDX expressions: "MIT OR Apache-2.0", "MIT AND BSD-3-Clause"
        licenses = []
        parts = re.split(r"\s+(?:OR|AND)\s+", license_expr, flags=re.IGNORECASE)
        
        for part in parts:
            cleaned = part.strip().strip("()")
            if cleaned:
                licenses.append(cleaned)
        
        return licenses if licenses else [license_expr.strip()]
    
    def _clean_license_token(self, token: str) -> Optional[str]:
        """Clean and normalize a license token."""
        if not token:
            return None
        
        # Remove common prefixes/suffixes
        cleaned = token.strip()
        cleaned = re.sub(r"^license[:\s]+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[:\s]+license$", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        # Normalize common variations
        replacements = {
            "apache 2": "Apache-2.0",
            "apache2": "Apache-2.0",
            "apache-2": "Apache-2.0",
            "bsd-2": "BSD-2-Clause",
            "bsd-3": "BSD-3-Clause",
            "bsd2": "BSD-2-Clause",
            "bsd3": "BSD-3-Clause",
        }
        
        cleaned_lower = cleaned.lower()
        for key, value in replacements.items():
            if key in cleaned_lower:
                cleaned = value
                break
        
        return cleaned if cleaned else None
    
    def _extract_licenses_from_text(self, text: str) -> List[str]:
        """Extract license mentions from text content."""
        if not text:
            return []
        
        licenses: Set[str] = set()
        
        # Common license patterns
        patterns = [
            r"(?:license|licensed)\s*(?:under|is)?\s*:?\s*([A-Z][A-Za-z0-9\-\s\.]+)",
            r"SPDX[-\s]License[-\s]Identifier:\s*([A-Z][A-Za-z0-9\-\s\.]+)",
            r"@license\s+([A-Z][A-Za-z0-9\-\s\.]+)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                license_text = match.group(1).strip()
                cleaned = self._clean_license_token(license_text)
                if cleaned:
                    licenses.add(cleaned)
        
        return sorted(licenses)
    
    def check_license(
        self,
        license_expr: Optional[str] = None,
        crate_api_data: Optional[dict] = None,
        documentation_text: Optional[str] = None,
    ) -> LicenseCheckResult:
        """
        Check if a crate's license is allowed.
        
        Args:
            license_expr: SPDX license expression from Cargo.toml or API
            crate_api_data: Full crate API data (may contain license field)
            documentation_text: Text content to search for license mentions
            
        Returns:
            LicenseCheckResult with detection and validation status
        """
        detected_licenses: Set[str] = set()
        
        # Extract from license expression
        if license_expr:
            for license_token in self._split_license_expression(license_expr):
                cleaned = self._clean_license_token(license_token)
                if cleaned:
                    detected_licenses.add(cleaned)
        
        # Extract from API data
        if crate_api_data:
            crate_section = crate_api_data.get("crate") or {}
            api_license = crate_section.get("license")
            if api_license:
                for license_token in self._split_license_expression(api_license):
                    cleaned = self._clean_license_token(license_token)
                    if cleaned:
                        detected_licenses.add(cleaned)
        
        # Extract from documentation
        if documentation_text:
            text_licenses = self._extract_licenses_from_text(documentation_text)
            for license_token in text_licenses:
                cleaned = self._clean_license_token(license_token)
                if cleaned:
                    detected_licenses.add(cleaned)
        
        detected_list = sorted(detected_licenses)
        
        if not detected_list:
            return LicenseCheckResult(
                detected_licenses=[],
                status="unknown",
                message="No license information detected",
                confidence=0.0,
            )
        
        # Check for forbidden licenses
        forbidden = []
        for license_name in detected_list:
            license_lower = license_name.lower()
            # Check against denied list
            if any(denied in license_lower for denied in self.denied_licenses):
                forbidden.append(license_name)
        
        if forbidden:
            return LicenseCheckResult(
                detected_licenses=detected_list,
                status="forbidden",
                message=f"Detected disallowed license(s): {', '.join(forbidden)}",
                confidence=1.0,
            )
        
        # Check if explicitly allowed
        if self.require_explicit_allow:
            if self.allowed_licenses:
                # Check if any detected license is in allowed list
                allowed_found = any(
                    license_name.lower() in self.allowed_licenses
                    for license_name in detected_list
                )
                if not allowed_found:
                    return LicenseCheckResult(
                        detected_licenses=detected_list,
                        status="warning",
                        message=f"License(s) not in allowed list: {', '.join(detected_list)}",
                        confidence=0.8,
                    )
            else:
                # Check against default allowed patterns
                matches_pattern = any(
                    pattern.match(license_name)
                    for license_name in detected_list
                    for pattern in self.allowed_patterns
                )
                if not matches_pattern:
                    return LicenseCheckResult(
                        detected_licenses=detected_list,
                        status="warning",
                        message=f"License(s) may require review: {', '.join(detected_list)}",
                        confidence=0.7,
                    )
        
        # All checks passed
        return LicenseCheckResult(
            detected_licenses=detected_list,
            status="allowed",
            message=f"All detected licenses comply with policy: {', '.join(detected_list)}",
            confidence=0.9 if detected_list else 0.5,
        )


def create_default_license_filter() -> LicenseFilter:
    """Create a license filter with default settings."""
    return LicenseFilter(
        allowed_licenses=None,  # Use pattern matching
        denied_licenses=DISALLOWED_LICENSE_SUBSTRINGS,
        require_explicit_allow=False,
    )


def create_strict_license_filter(allowed_licenses: List[str]) -> LicenseFilter:
    """Create a strict license filter that only allows specified licenses."""
    return LicenseFilter(
        allowed_licenses=allowed_licenses,
        denied_licenses=DISALLOWED_LICENSE_SUBSTRINGS,
        require_explicit_allow=True,
    )

