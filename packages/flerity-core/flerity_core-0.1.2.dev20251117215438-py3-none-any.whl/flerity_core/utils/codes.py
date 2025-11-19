"""Utilities for secure code generation."""

import secrets
import string


def generate_invitation_code(prefix: str = "INV") -> str:
    """Generate secure invitation code.
    
    Args:
        prefix: Code prefix (default: "INV")
        
    Returns:
        Secure invitation code in format PREFIX-XXXXXXXX
    """
    # 8 random uppercase letters and digits
    random_part = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(8)
    )
    return f"{prefix}-{random_part}"
