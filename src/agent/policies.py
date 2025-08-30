import re
from typing import List


class Policy:
    def check_pii(self, text: str) -> List[str]:
        """Checks for PII in a given text (e.g., email addresses)."""
        pii = []
        # Simple regex for email addresses
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if emails:
            pii.extend(emails)
        return pii

    def check_naming_conventions(self, name: str) -> bool:
        """Checks if a name follows the configured naming conventions."""
        # Placeholder implementation
        return True

    def check_review_gates(self, compile_status: bool, test_status: bool) -> bool:
        """Checks if the review gates (compile and test) are passed."""
        # Placeholder implementation
        return compile_status and test_status


policy = Policy()
