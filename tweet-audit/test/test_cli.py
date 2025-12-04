import pytest
from unittest.mock import patch, Mock
from src.cli import main
import sys
from src.schema import Result

def test_show_help_when_no_args_given(capsys):
    sys.argv = ["main.py"]
    main()
    captured = capsys.readouterr()
    assert "usage:" in captured.out
    

@patch("src.cli.AuditService")
def test_extract_tweet_when_extract_command_is_passed(mock_audit_class):
    mock_instance = mock_audit_class.return_value
    mock_instance.extract_tweet.return_value = Result(success=True, count=10)
    
    #mock the cli
    sys.argv = ["main.py", "extract-tweets"]
    main()
    mock_instance.extract_tweets.assert_called_once()
    
@patch("src.cli.AuditService")
def test_analyis_tweet_when_analyze_command_is_passed(mock_audit_class):
    mock_instance = mock_audit_class.return_value
    mock_instance.analyze_tweets.return_value = Result(success=True, count=10)
    
    #mock the cli
    sys.argv = ["main.py", "analyze-tweets"]
    main()
    mock_instance.analyze_tweets.assert_called_once()
    
    
@pytest.mark.parametrize(
    "error_type,error_message",
    [
        ("analysis_failed", "API error occurred"),
        ("file_not_found", "CSV file not found")
    ],
)
@patch("src.cli.AuditService")
def test_handle_analysis_errors_gracefully(
    mock_audit_class, capsys, error_type, error_message
):
    mock_instance = mock_audit_class.return_value
    mock_instance.analyze_tweets.return_value = Result(
        success=False, error_type=error_type, error_message=error_message
    )
    sys.argv = ["main.py", "analyze-tweets"]

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
        
@pytest.mark.parametrize(
    "error_type,error_message",
    [
        ("file_not_found", "Archive not found"),
        ("invalid_format", "Invalid JSON format"),
    ],
)
@patch("src.cli.AuditService")
def test_handle_extact_errors_gracefully(
    mock_audit_class, capsys, error_type, error_message
):
    mock_instance = mock_audit_class.return_value
    mock_instance.extract_tweets.return_value = Result(
        success=False, error_type=error_type, error_message=error_message
    )
    sys.argv = ["main.py", "extract-tweets"]

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1