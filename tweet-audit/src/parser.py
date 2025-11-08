from schema import Tweets
from abc import ABC, abstractmethod
import json 
from config import setup_logger

logger = setup_logger("parser", "parser.log")

class Parser(ABC):
    #abstract parent class which enforces all child class implement this method
    @abstractmethod
    def parse(self) -> list[Tweets]:
        pass
    
#keys in json
ID_FIELD = "id_str"
CONTENT_FIELD = "full_text"

class JsonParser(Parser):
    #this class handles parsing the json to extract the id and full text field
    def __init__(self, file_path:str):
        self.file_path = file_path
        
    def parse(self)-> list[Tweets]:
        try:
            with open (self.file_path, encoding="utf-8") as f:
                data = json.load(f)
                return list(
                    Tweets(
                        id=field["tweet"][ID_FIELD],
                        content=field["tweet"][CONTENT_FIELD]
                    )
                    for field in data
                )
        except Exception as e:
            logger.error(f"an error occurred: {str(e)}")
            raise Exception(f"an error occurred: {str(e)}") 

class CSVparser(Parser):
    def parse(self):
        return super().parse()