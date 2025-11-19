"""Utility functions for the TUI."""
import re
import uuid
from pathlib import Path
from typing import Optional

def is_valid_repo_name(name: str) -> bool:
    """Check if a repository name is valid.
    
    Allows most common characters while preventing:
    - Path separators (\ /)
    - Wildcards (* ?)
    - Quotes and other problematic characters
    """
    # Disallowed characters that could cause issues
    # \ / : * ? " < > |
    if any(c in name for c in '\\/:*?"<>|'):
        return False
        
    # Basic length check
    if not (0 < len(name) <= 100):
        return False
        
    # Must contain at least one non-whitespace character
    if not name.strip():
        return False
        
    return True

def safe_id(name: str) -> str:
    """Generate a unique widget ID from a repository name."""
    # Create a unique ID using UUID
    unique_id = str(uuid.uuid4())
    # Also include a sanitized version of the name for debugging
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:20]  # Limit length
    return f'repo-{safe_name}-{unique_id}'

def resolve_path(path: str) -> Optional[Path]:
    """Resolve and validate a filesystem path."""
    try:
        return Path(path).expanduser().resolve()
    except (OSError, RuntimeError):
        return None
