#this module handle parsing of files, read and write operations
from schema import Tweets, AnalysisResult
from abc import ABC, abstractmethod
import json 
from utils import ensure_dir_and_file
import csv
from typing import List
from pathlib import Path
from config import setup_logger
logger = setup_logger(__name__, "parser.log")

class Parser(ABC):
    #abstract parent class which enforces all child class implement this method
    @abstractmethod
    def parse(self) -> list[dict]:
        pass
    
#keys in json
ID_FIELD = "id_str"
CONTENT_FIELD = "full_text"


#buffer csv to hold extracted id and content
EXTRACTED_ID = "id"
EXTRACTED_CONTENT_FIELD = "content"

TWEET_URL = "tweet_url"
DELETE_TWEET = "deleted"

FILE_ENCODING="utf=8"
class JsonParser(Parser):
    #this class handles parsing the json to extract the id and full text field
    def __init__(self, file_path:str):
        self.file_path = file_path
    

    def parse(self) -> list[dict]:
        try:
            if not Path(self.file_path).exists():
                logger.error(f"File {self.file_path} does not exist.")
                raise FileNotFoundError(f"File not found or could not be created: {self.file_path}")

            with open(self.file_path, encoding=FILE_ENCODING) as f:
                data = json.load(f)
                return [
                    Tweets(
                        id=field["tweet"][ID_FIELD],
                        content=field["tweet"][CONTENT_FIELD]
                    ).model_dump()
                    for field in data
                ]
        except FileNotFoundError as e:
            logger.error(f"File not found error during parsing: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in {self.file_path}: {e}")
            raise ValueError(f"Invalid JSON format in {self.file_path}") from e
        except KeyError as e:
            logger.error(f"Missing key in JSON data: {e}. Check ID_FIELD and CONTENT_FIELD.")
            raise ValueError(f"Missing expected key in JSON data: {e}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred while parsing {self.file_path}")
            raise Exception(f"Failed to parse {self.file_path}: {e}") from e

class CSVparser(Parser):
    def __init__(self, file_path):
        self.file_path = file_path
    def parse(self) -> list[dict]:
        #this method reads the CSV
        try:
            dir_created, file_created = ensure_dir_and_file(self.file_path)
            if dir_created:
                logger.info(f"Directory for {self.file_path} was created.")
            if file_created:
                logger.info(f"File {self.file_path} was created.")

            if not Path(self.file_path).exists():
                logger.error(f"File {self.file_path} does not exist after ensure_dir_and_file.")
                raise FileNotFoundError(f"File not found or could not be created: {self.file_path}")

            with open(self.file_path, "r", newline="", encoding=FILE_ENCODING) as f:
                reader = csv.DictReader(f)
                tweets_list = [
                    Tweets(id=row[EXTRACTED_ID], content=row[EXTRACTED_CONTENT_FIELD]).model_dump()
                    for row in reader
                ]
                logger.info(f"Successfully read {len(tweets_list)} rows from CSV file: {self.file_path}")
                return tweets_list
        except FileNotFoundError as e:
            logger.error(f"File not found error during CSV parsing: {e}")
            raise 
        except KeyError as e:
            logger.error(f"Missing key in CSV header: {e}. Expected '{EXTRACTED_ID}' and '{EXTRACTED_CONTENT_FIELD}'.")
            raise AttributeError(f"Missing expected column in CSV: {e}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred while parsing CSV {self.file_path}")
            raise Exception(f"Failed to parse CSV {self.file_path}: {e}") from e
            
class CSVwriter():
    def __init__(self, file_path:str, append:bool=False):
        self.file_path=file_path
        self.append=append
    
    # we have the dunder __enter__ (Called when the with block starts and Returns whatever you want to assign to the variable after as.)

    def __enter__(self) -> "CSVwriter":
        dir_created, file_created = ensure_dir_and_file(self.file_path)
        if dir_created:
            logger.info(f"Directory for {self.file_path} was created by CSVwriter.")
        if file_created:
            logger.info(f"File {self.file_path} was created by CSVwriter.")
        
        if not Path(self.file_path).exists():
            logger.error(f"File {self.file_path} does not exist after ensure_dir_and_file in CSVwriter __enter__.")
            raise FileNotFoundError(f"File not found or could not be created: {self.file_path}")

        self.header_written = self.append and Path(self.file_path).stat().st_size > 0

        mode = "a" if self.append and Path(self.file_path).exists() else "w"
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
            logger.warning("file has been closed")
        if exc_type:
            logger.error(f"An error occured: {exc_type}, {exc_value}", exc_info=traceback) 
        return False
             
    
    def write_tweets(self, tweets: List[dict]):
        """
        Writes the id and content from a list of Tweets into the CSV file.
        """
        logger.info(f"Attempting to write {len(tweets)} tweets to {self.file_path}")
        try:
            if not self.writer:
                logger.error(f"CSV writer is not initialized for {self.file_path}.")
                raise RuntimeError("CSV file is not open")
            
            if not self.header_written:
                self.writer.writerow([EXTRACTED_ID, EXTRACTED_CONTENT_FIELD])
                self.header_written = True
                logger.info(f"CSV header written to {self.file_path}.")

            for tweet in tweets:
                validated_tweets = Tweets(**tweet)
                self.writer.writerow([validated_tweets.id, validated_tweets.content])
            logger.info(f"Successfully wrote {len(tweets)} tweets to {self.file_path}.")
        except RuntimeError:
            raise
        except Exception as e:
            logger.exception(f"An error occurred while writing tweets to {self.file_path}")
            raise Exception(f"Failed to write tweets to CSV: {e}") from e

    
    def write_analysed_tweets(self, **tweet_data: dict):
        """
        Writes the analysis result of a tweet to the CSV file.
        """
        logger.info(f"Attempting to write analysed tweet data to {self.file_path}")
        try:
            validated_tweet_data = AnalysisResult(**tweet_data)
            if not self.writer:
                logger.error(f"CSV writer is not initialized for {self.file_path}.")
                raise RuntimeError("CSVWriter is not open")

            if not self.header_written:
                self.writer.writerow([TWEET_URL, DELETE_TWEET])
                self.header_written = True
                logger.info(f"CSV header for analysed tweets written to {self.file_path}.")

            self.writer.writerow([validated_tweet_data.tweet_url, validated_tweet_data.deleted])
            self.file.flush() 
            logger.info(f"Successfully wrote analysed tweet data for {validated_tweet_data.tweet_url} to {self.file_path}.")
        except RuntimeError:
            raise
        except Exception as e:
            logger.exception(f"An error occurred while writing analysed tweet data to {self.file_path}")
            raise Exception(f"Failed to write analysed tweet data to CSV: {e}") from e


class Checkpoint:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.file = None

    def __enter__(self) -> "Checkpoint":
        dir_created, file_created = ensure_dir_and_file(self.file_path)
        if dir_created:
            logger.info(f"Directory for {self.file_path} was created by checkpoint.")
        if file_created:
            logger.info(f"File {self.file_path} was created by checkpoint.")
        self.file = open(self.file_path, "a+", encoding=FILE_ENCODING)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self.file:
            self.file.close()
            self.file = None
        return False

    def load(self) -> int:
        if not self.file:
            raise RuntimeError("Checkpoint file is not open")

        self.file.seek(0)
        content = self.file.read().strip()

        if not content:
            return 0

        try:
            return int(content)
        except ValueError as e:
            raise ValueError(
                f"Corrupted checkpoint file {self.file_path}: expected integer, got '{content}'"
            ) from e

    def save(self, tweet_index: int) -> None:
        if not self.file:
            raise RuntimeError("Checkpoint file is not open")

        self.file.seek(0)
        self.file.truncate()
        self.file.write(str(tweet_index))
        self.file.flush()