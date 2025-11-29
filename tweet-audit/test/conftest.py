import pytest
from src.config import Settings, env_config
from src.ai_setup import AI_Setup

@pytest.fixture
def settings():
    return Settings(
        
    )


@pytest.fixture
def configure_AI_setup():
    return AI_Setup()

@pytest.fixture
def test_config():
    return {
        "test_gemini_key": "12345det"
    }