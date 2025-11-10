from functools import wraps
import time
from google import genai
from config import env_config
from exception import EnvironmentVariableError
from prompt import SYSTEM_PROMPT
from schema import AgentResponse
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


class AI_Setup():
    def __init__(self):
        self.gemini_key = env_config.GOOGLE_API_KEY
        if not self.gemini_key:
            raise EnvironmentVariableError("google api key not found in enironment variable")
        self.client = genai.Client(api_key=self.gemini_key)
        self.config = self.client.types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT
    )
        

        
    
    def parse_tweets(self, tweets:dict)->dict:
        response = self.client.models.generate_content(
            model=env_config.MODEL_NAME,
            contents=tweets
        )
        validated_response = AgentResponse(response.text).model_dump()
        return validated_response
    
    


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