from pydantic import BaseModel

class Tweets(BaseModel):
    id:str
    content:str


class AgentResponse(BaseModel):
    id:str
    content:str
    should_delete:bool=False
    reason:str
    
class AnalysisResult(BaseModel):
    tweet_url: str
    deleted: bool = False


class AnalysisResponse(BaseModel):
    pass 

class Settings():
    tweets_archive_path: str = "data/tweets.json"
    base_twitter_url: str = "https://x.com"
    
    
class Result(BaseModel):
    success: bool = False
    count: int = 0
    error_type: str = ""
    error_message: str = ""
    
    