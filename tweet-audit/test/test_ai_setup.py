from src.config import env_config
from src.ai_setup import AI_Setup

def test_env_loaded_successfully():
    ai_setup = AI_Setup()
    assert env_config.GOOGLE_API_KEY == getattr(ai_setup, "gemini_key")
    
