from config import settings
from utils import ensure_dir_and_file

ensure_dir_and_file(settings.checkpoint_path)
with open(settings.checkpoint_path) as f:
    print("file is opened")