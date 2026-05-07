import json
import csv 
from src.parser import CSVparser, CSVwriter, JsonParser, Checkpoint
import pytest
from unittest.mock import Mock, patch 
from src.schema import Tweets, AgentResponse

def test_parse_json_from_file(testdata_dir):
    parser = JsonParser(str(testdata_dir / "tweet.json"))
    tweets = parser.parse() 
    assert (len(tweets)) == 3
    

def test_json_file_not_found(testdata_dir):
    parser = JsonParser(str(testdata_dir / "notfound.json"))
    with pytest.raises(FileNotFoundError):
        parser.parse()
        

def test_invalid_json(testdata_dir):
    parser = JsonParser(str(testdata_dir / "invalid.json")) 
    with pytest.raises(ValueError, match="Invalid JSON format"):
        parser.parse()


def test_read_tweet_from_csv(testdata_dir):
    parser =  CSVparser(str(testdata_dir / "tweet.csv")) 
    tweet = parser.parse()
    len(tweet)
    

@patch("src.parser.ensure_dir_and_file")
def test_csv_file_not_found(mock_ensure, testdata_dir): 
    mock_ensure.side_effect = FileNotFoundError("Simulated file not found Error") 
    parser = CSVparser(str(testdata_dir / "not_exist.csv")) 
    with pytest.raises(FileNotFoundError):
        parser.parse()


def test_incomplete_csv_fields(testdata_dir):
    parser =  CSVparser(str(testdata_dir / "invalid.csv"))  
    with pytest.raises(AttributeError):
        parser.parse()
    

def test_return_zero_when_checkpoint_file_empty(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.txt"

    with Checkpoint(str(checkpoint_path)) as cp:
        value = cp.load()

    assert value == 0
    
    
def test_should_save_and_load_checkpoint_value(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.txt"

    with Checkpoint(str(checkpoint_path)) as f:
        f.save(20)
    with Checkpoint(str(checkpoint_path)) as f:
        value = f.load()
    assert value == 20
    

def test_raise_error_when_checkpoint_content_invalid(tmp_path):
    checkpoint_path = tmp_path / "invalid.txt"
    checkpoint_path.write_text("string")

    with Checkpoint(str(checkpoint_path)) as f:
        with pytest.raises(ValueError, match="Corrupted checkpoint"):
            f.load()

def test_should_write_tweets_to_csv_file(tmp_path):
    output_path = tmp_path / "output.csv"
    tweets =[
        {"id": "123", "content": "First tweet"},
        {"id": "456", "content": "Second tweet"},
    ]

    with CSVwriter(str(output_path)) as writer:
        writer.write_tweets(tweets)

    with open(output_path, newline="") as f:
        reader = csv.reader(f)
   