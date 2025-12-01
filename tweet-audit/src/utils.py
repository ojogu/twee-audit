#util file to handle dir/file exist, clean json file from gemini

import json
from pathlib import Path
import re
from config import setup_logger

logger = setup_logger(__name__, "utils.log")

def ensure_dir_and_file(path_str: str) -> tuple[bool, bool]:
    """
    Ensures that the directory for the given path exists and the file itself exists.
    If the directory or file does not exist, it will be created.
    Returns a tuple of (dir_created: bool, file_created: bool)
    """
    path = Path(path_str)
    dir_created = False
    file_created = False

    # Ensure directory exists
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path.parent}")
        dir_created = True
    else:
        logger.info(f"Directory exists: {path.parent}")

    # Ensure file exists
    if not path.exists():
        path.touch(exist_ok=True)
        logger.info(f"Created new file: {path}")
        file_created = True
    else:
        logger.info(f"File already exists: {path}")
    
    return dir_created, file_created


def parse_and_clean_json(json_string):

    if not isinstance(json_string, str):
        raise TypeError("Input must be a string")
    
    # Remove leading/trailing whitespace
    cleaned = json_string.strip()
    
    # Remove markdown code fences (```json, ```, ```python, etc.)
    cleaned = re.sub(r'^```(?:json|python|javascript|js)?\s*\n?', '', cleaned)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned)
    
    # Remove any remaining backticks at start/end
    cleaned = cleaned.strip('`').strip()
    
    # Normalize whitespace (multiple spaces/newlines to single space)
    # But preserve structure inside the JSON
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Try to parse the cleaned JSON
    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError as e:
        # If parsing fails, try one more time with more aggressive cleaning
        # Remove all whitespace except within strings
        try:
            # This is a last resort - removes formatting but may help
            compressed = ''.join(cleaned.split())
            parsed = json.loads(compressed)
            return parsed
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON: {e}") from e
