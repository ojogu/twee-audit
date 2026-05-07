import pytest
from src.config import Settings, Config
from src.ai_setup import AI_Setup
from pathlib import Path
from src.schema import Tweets, AgentResponse

TESTDATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture
def testdata_dir():
    return TESTDATA_DIR


@pytest.fixture
def settings():
    return Settings(
        base_twitter_url="https://x.com",
        x_username="testuser",
    )
    
@pytest.fixture
def test_tweet_data():
    return Tweets(
        id="1234",
        content="I want to be a cracked Engineer",
    ).model_dump()
    
@pytest.fixture
def test_system_prompt():
    return "test system prompt"






@pytest.fixture
def test_config():
    return Config(
        GOOGLE_API_KEY="test-key",
        MODEL_NAME="gemini-test",
    )