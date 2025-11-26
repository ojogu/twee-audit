import pytest
from unittest.mock import Mock

user_data = Mock()
user_data.get_users.return_value = {}
def test_should_analyze_tweet_with_delete_decision(mock_settings):
    pass 