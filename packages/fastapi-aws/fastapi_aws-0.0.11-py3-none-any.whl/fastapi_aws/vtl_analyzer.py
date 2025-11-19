import re
from typing import Dict


class VTLAnalyzer:
    """Analyzes VTL templates to determine required request parameters

    These must be explicitly passed by the integration.
    """

    # Patterns for different VTL context variables
    VTL_PATTERNS = {
        "header": re.compile(r'\$input\.params\([\'"]([^"\']+)["\']\)'),
        "query": re.compile(r'\$input\.params\([\'"]([^"\']+)["\']\)'),  # same as header
        "path": re.compile(r'\$input\.path\([\'"]([^"\']+)["\']\)'),
        # Context variables don't need request_parameters - they're always available
    }

    @classmethod
    def extract_request_dependencies(cls, *templates: str) -> Dict[str, Dict[str, str]]:
        """Extract required request_parameters from VTL templates.

        Args:
            *templates: VTL template strings to analyze

        Returns:
            Dict mapping integration.request.* to method.request.*
        """
        request_parameters = {}

        for template in templates:
            if not template:
                continue

            # Find all $input.params() references
            for match in cls.VTL_PATTERNS["header"].finditer(template):
                param_name = match.group(1)
                # Map both as header and query parameter (API Gateway checks both)
                request_parameters[f"integration.request.header.{param_name}"] = f"method.request.header.{param_name}"
                request_parameters[f"integration.request.querystring.{param_name}"] = f"method.request.querystring.{param_name}"

        return request_parameters
