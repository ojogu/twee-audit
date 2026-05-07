#this module handles Ai integration with gemini, handling retry logic 

from functools import wraps
import time
from google import genai
from google.genai.types import GenerateContentConfig
from config import env_config
from src.application_exception import EnvironmentVariableError, APIerror
from prompt import SYSTEM_PROMPT
from schema import AgentResponse
from config import setup_logger
import json
from utils import parse_and_clean_json
from pydantic import ValidationError


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0):
    """Retry decorator with exponential backoff for transient errors"""

    def decorator(func):
        @wraps(func) #func is the function that function that will be retried i.e the function we place the decorator on
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs) #try to returns if success
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower() 
                    is_retryable = any(
                        keyword in error_str
                        for keyword in [
                            "timeout",
                            "connection",
                            "rate limit",
                            "quota",
                            "503",
                            "429",
                            "unavailable",
                            "temporarily unavailable",
                        ]
                    ) #converts error to str, Determine if the error is retryable. a generator expression that loops through each keyword in that list and checks if it appears inside the error_str.
                    #its efficient here because it would not build the list at once in memory, rather generate one-by-one

                    if not is_retryable or attempt == max_retries - 1: #If the error is not retryable or we’re on the last attempt
                        raise

                    sleep_time = delay * (2**attempt) + (time.time() % 1) #exponetial backoff logic
                    time.sleep(sleep_time) #Sleep before retrying

            raise last_exception

        return wrapper

    return decorator


logger = setup_logger(__name__, "ai_setup.log")

class AI_Setup():
    def __init__(self):
        self.gemini_key = env_config.GOOGLE_API_KEY
        if not self.gemini_key:
            logger.error("Google API key not found in environment variables.")
            raise EnvironmentVariableError("Google API key not found in environment variable")
        logger.info("Google API key successfully loaded.")
        
        self.client = genai.Client(api_key=self.gemini_key)
        logger.info("Google Gemini client initialized.")
        
        self.config = GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        logger.info("Gemini content generation configuration set with system instruction.")

    @retry_with_backoff()
    def analysis_tweets(self, tweets: dict) -> dict:
        try:
            #convert the dict to a string for compartiablity with gemini
            input_string = f"TWEET_ID: {tweets["id"]}\nTWEET_TEXT: {tweets["content"]}"
            
            response = self.client.models.generate_content(
                model=env_config.MODEL_NAME,
                contents=input_string,
                config=self.config # Use the configured generation_config
            )
            logger.info("Received response from Gemini model.")
            
            logger.debug(f"Raw Gemini response: {response.text}")

            try:
                parsed = parse_and_clean_json(response.text)
                logger.debug(f"cleaned response: {parsed}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from Gemini response: {e}")
                raise

            try:
                validated = AgentResponse.model_validate(parsed).model_dump()
            except Exception as e:
                logger.exception(f"Failed to validate response dict: {e}")
                raise
            logger.info("Gemini response successfully validated.")
            return validated

        except EnvironmentVariableError as e:
            logger.error(f"Environment variable error: {e}")
            raise
        except RuntimeError as e:
            logger.error(f"API connection failed: {e}")
            raise APIerror("API connection failed")
        
        except Exception as e:
            logger.exception(f"An error occurred during Gemini content generation or response validation: {e}")
            raise Exception(f"Failed to parse tweets with AI: {e}") from e
    
    


""" 
Step-by-step mental flow 🔄

1️⃣ any() starts
Python sees a generator expression inside any(),
so it doesn’t build a list — it starts pulling values one by one.

2️⃣ Generator runs the first iteration

keyword = "timeout"

Checks "timeout" in error_str → ✅ True

The generator yields this value to any()

Now, any() receives True.

3️⃣ any() logic

As soon as any() sees one True value,
it stops immediately.
(This is called short-circuiting.)

It doesn’t bother calling the generator again.

It returns True.


| Step | Who acts  | What happens                                              |
| ---- | --------- | --------------------------------------------------------- |
| 1    | `any()`   | Starts asking the generator for the next value            |
| 2    | Generator | Runs one check (`keyword in error_str`) and yields result |
| 3    | `any()`   | If result == True → stop immediately (short-circuit)      |
| 4    | Otherwise | Ask for the next value                                    |
| 5    | End       | Return True if any True was seen, else False              |

"""
