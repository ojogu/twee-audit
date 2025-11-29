from src.config import env_config
from src.ai_setup import AI_Setup
import pytest 
from src.application_exception import EnvironmentVariableError
from unittest.mock import Mock, patch 

def test_env_loaded_successfully(configure_AI_setup):
    # ai_setup = AI_Setup()
    assert env_config.GOOGLE_API_KEY == getattr(configure_AI_setup, "gemini_key")

@patch("src.ai_setup.env_config")
def test_key_not_found(mock_env_config):
    mock_env_config.GOOGLE_API_KEY  = None
    with pytest.raises(EnvironmentVariableError):
        AI_Setup()
        #this means that this test must throw the exception i.e if the exception is raised, the test pass. else if it doesn't throw the exception, the tests fails

# @patch("src.ai_setup.env_config")
# def test_key_not_found(mock_env_config):
#     from src.exception import EnvironmentVariableError as TestException
#     from src.ai_setup import AI_Setup
    
#     # Check if AI_Setup uses the same exception class
#     import src.ai_setup as ai_module
#     print(f"Test exception class: {TestException}")
#     print(f"Test exception id: {id(TestException)}")
    
#     mock_env_config.GOOGLE_API_KEY = None
    
#     with pytest.raises(TestException):
#         AI_Setup()