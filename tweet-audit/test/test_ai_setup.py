from src.config import env_config
from src.ai_setup import AI_Setup
import pytest 
from src.application_exception import EnvironmentVariableError
from unittest.mock import Mock, patch 
from src.config import setup_logger
logger = setup_logger(__name__, "main.log")

def test_env_loaded_successfully():
    ai_setup = AI_Setup() 
    assert env_config.GOOGLE_API_KEY == ai_setup.gemini_key

@patch("src.ai_setup.env_config")
def test_key_not_found(mock_env_config):
    mock_env_config.GOOGLE_API_KEY  = None
    with pytest.raises(EnvironmentVariableError):
        AI_Setup()
        #this means that this test must throw the exception i.e if the exception is raised, the test pass. else if it doesn't throw the exception, the tests fails

@patch("src.ai_setup.GenerateContentConfig")
@patch("src.ai_setup.env_config")
@patch("src.ai_setup.genai.Client")
def test_analyze_tweet_with_delete_decision(mock_genai_client_class, mock_env_config, mock_config, settings, test_config, test_system_prompt, test_tweet_data):
    mock_env_config.GOOGLE_API_KEY  = test_config.GOOGLE_API_KEY
    mock_env_config.MODEL_NAME = test_config.MODEL_NAME
    mock_client_instance = mock_genai_client_class.return_value #instance of patched client
    #mock response
    response = mock_client_instance.models.generate_content.return_value 
    response.text = '{"decision": "DELETE", "reason": "Contains profanity"}'
    
    # mock_config.assert_called_once_with(system_instruction=test_system_prompt)
    
    ai_setup = AI_Setup()
    ai_setup.analysis_tweets(test_tweet_data)

    
    
    
