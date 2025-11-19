"""
DSL Pipeline - Phase 4: Memory Validation.

Validates ParsedMemory objects against TemplateSpec requirements.
This is the validation gate before Phase 3 (rendering).

Uses the validation functions from validators/validate_dsl.py and raises
Phase4Error with collected issues if validation fails.

Key Class:
- MemoryValidator: Main validator with validate() method

Validation Logic:
- Calls validators/validate_dsl.py functions (simple functions returning issues)
- Collects all validation issues
- Raises Phase4Error if any issues found (fail_fast=False collects all)
- Returns silently if validation passes (no news = good news)

Example:
    validator = MemoryValidator(template_spec)
    validator.validate(parsed_memory, fail_fast=True)  # Raises on first error
    validator.validate(parsed_memory, fail_fast=False)  # Collects all errors
"""

import logging

from reerelease.errors import Phase4Error
from reerelease.validators.validate_dsl import validate_parsed_memory

from .phase1_specs import TemplateSpec
from .phase2_parser import ParsedMemory


class MemoryValidator:
    """
    Validator for ParsedMemory objects against TemplateSpec.

    Uses validation functions from validators/validate_dsl.py to check:
    - Required fields and sections present
    - Field formats (date, int, float, enum)
    - Field patterns (regex)
    - Section requirements

    Raises Phase4Error with collected issues if validation fails.
    """

    def __init__(self, spec: TemplateSpec):
        """
        Initialize validator with template specification.

        Args:
            spec: Template specification defining requirements
        """
        self.log = logging.getLogger("dslp4")
        self.spec = spec

    def validate(self, memory: ParsedMemory, fail_fast: bool = True) -> None:
        """
        Validate ParsedMemory against TemplateSpec.

        Args:
            memory: Parsed memory to validate
            fail_fast: If True, raise on first error. If False, collect all errors.

        Raises:
            Phase4Error: If validation finds any issues

        Note:
            Following the "no news = good news" pattern from validators/*.py
            This method either returns silently (valid) or raises (invalid).
        """
        self.log.debug(
            f"Validating memory with {len(memory.fields)} fields, {len(memory.sections)} sections"
        )
        # Call the validation function from validators/validate_dsl.py
        issues = validate_parsed_memory(memory, self.spec)

        if issues:
            self.log.warning(f"Validation found {len(issues)} issue(s)")
        else:
            self.log.info("Memory validation passed")

        # If fail_fast, only keep first error
        if fail_fast and issues:
            issues = [issues[0]]
            self.log.debug("fail_fast=True, keeping only first issue")

        # Raise if any issues found
        if issues:
            raise Phase4Error(
                message=f"Memory validation failed with {len(issues)} issue(s)",
                issues=issues,
            )

        # No news = good news
        # Validation passed, return silently
