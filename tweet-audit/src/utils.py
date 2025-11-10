from pathlib import Path
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
