import pytest
import requests

from boxing.utils.api_utils import get_random

RANDOM_NUMBER = 4

@pytest.fixture
def mock_random_org(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced a mock object
    mock_response = mocker.Mock()
    #We are giving that object a text attribute
    mock_response.text = f"{RANDOM_NUMBER}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(mock_random_org):
    """Test retrieving a random number from random.org.

    """
    result = get_random()

    # Assert that the result is the mocked random number

def test_get_random_request_failure(mocker):
    """Test handling of a request failure when calling random.org.

    """
    #simulate a request failure

def test_get_random_timeout(mocker):
    """Test handling of a timeout when calling random.org.

    """
    #Simulate a timeout

