import os
from schema import Tweets, AnalysisResult
from abc import ABC, abstractmethod
import json 
from config import setup_logger
from utils import ensure_dir_and_file
import csv
from typing import List
logger = setup_logger("parser", "parser.log")

class Parser(ABC):
    #abstract parent class which enforces all child class implement this method
    @abstractmethod
    def parse(self) -> list[Tweets]:
        pass
    
#keys in json
ID_FIELD = "id_str"
CONTENT_FIELD = "full_text"


#buffer csv to hold extracted id and content
EXTRACTED_ID = "id"
EXTRACTED_FIELD = "content"

TWEET_URL = "tweet_url"
DELETE_TWEET = "delete_tweet"
FILE_ENCODING="utf=8"
class JsonParser(Parser):
    #this class handles parsing the json to extract the id and full text field
    def __init__(self, file_path:str)->dict:
        self.file_path = file_path
    

    def parse(self)-> list[Tweets]:
        try:
            _, file = ensure_dir_and_file(self.file_path)
            if not file:
                raise Exception("an error occured") 
            with open (self.file_path, encoding=FILE_ENCODING) as f:
                data = json.load(f)
                return list(
                    Tweets(
                        id=field["tweet"][ID_FIELD],
                        content=field["tweet"][CONTENT_FIELD]
                    ).model_dump()
                    for field in data
                )
        except Exception as e:
            logger.error(f"an error occurred: {str(e)}")
            raise Exception(f"an error occurred: {str(e)}") 

class CSVparser(Parser):
    def __init__(self, file_path):
        self.file_path = file_path
    def parse(self):
        #this method reads the CSV
        try:
            _, file = ensure_dir_and_file(self.file_path)
            if not file:
                raise Exception("an error occured") 
            with open(self.file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                return [
                    Tweets(id=row[EXTRACTED_ID], content=row[EXTRACTED_FIELD])
                    for row in reader
                ]
        except Exception as e:
            logger.error(f"an error occured:{str(e)}")
            
    

class CSVwriter():
    def __init__(self, file_path:str, append:bool=False):
        self.file=file_path
        self.append=append
    
    #we have the dunder __enter__ (Called when the with block starts and Returns whatever you want to assign to the variable after as.)

    def __enter__(self) -> "CSVwriter":
        dir_path, file = ensure_dir_and_file(self.file_path)
        if not file:
            raise Exception() 
        # file_exists = os.path.exists(self.file_path)
        self.header_written = self.append and file

        mode = "a" if self.append and file else "w"
        self.file = open(self.file_path, mode, encoding=FILE_ENCODING, newline="")
        self.writer = csv.writer(self.file)
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        #  __exit__ Called when the with block ends, no matter what happens (normal completion or exception). 
        # # It’s where you do cleanup, close files, release resources, etc.
        # # If you return True, it tells Python to suppress any exceptions that occurred inside the block.
        if self.file:
            self.file.close()
            self.writer = None
            self.file=None
        if exc_type:
            logger.error(f"An error occured: {exc_type}, {exc_value}", exc_info=traceback) 
        return False
             
    
    def write_tweets(self, tweets:List[Tweets]):
        #write the id, content from the json into the csv file for easier processing
        if not self.writer:
            raise RuntimeError("CSV file is not open")
        if not self.header_written:
            self.writer.writerow([ID_FIELD, CONTENT_FIELD])
            self.header_written = True

        for tweet in tweets:
            validated_tweets = Tweets(tweet)
            self.writer.writerow([validated_tweets.id, validated_tweets.content])

    
    def write_analysed_tweets(self, tweet_data: AnalysisResult):
        #after the LLM analysis, this method writes the result to the result csv
        pass 
        
    
        
    