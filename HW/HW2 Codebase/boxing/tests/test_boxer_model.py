from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Create/Delete boxer
#
######################################################

def test_create_boxer(mock_cursor):
    """ Testing the create_boxer function
    """
    create_boxer(name= "Sean Zhang", weight= 175, height= 71, reach= 87.2, age= 18)
    
    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Sean Zhang", 175, 71, 87.2, 18)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_duplicate_boxer(mock_cursor):
    """ Testing the create_boxer function with a duplicate name 
    (should raise an error)
    """
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")

    with pytest.raises(ValueError, match=r"Boxer with name 'Sean Zhang' already exists"):
        create_boxer(name= "Sean Zhang", weight= 175, height= 71, reach= 87.2, age= 18)

def test_create_boxer_invalid_weight():
    """ Test error when creating a boxer with a weight < 125
    """
    with pytest.raises(ValueError, match=r"Invalid weight: 124\. Weight must be at least 125\."):
        create_boxer(name= "Sean Zhang", weight= 124, height= 71, reach= 87.2, age= 18)
        
def test_create_boxer_invalid_height():
    """ Test error when creating a boxer with a height <= 0
    """
    with pytest.raises(ValueError, match=r"Invalid height: 0\. Height must be greater than 0\."):
        create_boxer(name= "Sean Zhang", weight= 175, height= 0, reach= 87.2, age= 18)
    
def test_create_boxer_invalid_reach():
    """ Test error when creating a boxer with a reach <= 0
    """
    with pytest.raises(ValueError, match=r"Invalid reach: -2.0\. Reach must be greater than 0\."):
        create_boxer(name= "Sean Zhang", weight= 175, height= 71, reach= -2.0, age= 18)
    
def test_create_boxer_invalid_age():
    """ Test error when creating a boxer with an age < 18 or age > 40
    """
    with pytest.raises(ValueError, match=r"Invalid age: 10\. Must be between 18 and 40\."):
        create_boxer(name= "Sean Zhang", weight= 175, height= 71, reach= 87.2, age= 10)
        
    with pytest.raises(ValueError, match=r"Invalid age: 100\. Must be between 18 and 40\."):
        create_boxer(name= "Sean Zhang", weight= 175, height= 71, reach= 87.2, age= 100)

def test_delete_boxer(mock_cursor):
    """ Testing the delete_boxer function
    """
    # Simulate the existence of a Boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)
    
    delete_boxer(1)
    
    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."

def test_delete_boxer_bad_id(mock_cursor):
    """ Testing the delete_boxer function with an ID representing no boxer 
    (should raise an error)
    """
    # Simulate no boxer exists with a given ID
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)
        
######################################################
#
#    Get Leaderboard
#
######################################################

def test_get_leaderboard_by_wins(mock_cursor):
    """ Testing the get_leaderboard function using the wins parameter
    """
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'name': "Sean Zhang", 'weight': 175, 'height': 71, 'reach': 87.2, 'age': 19, 'fights': 10, 'wins': 6},
        {'id': 4, 'name': "Peter Griffin", 'weight': 400, 'height': 75, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 4},
        {'id': 2, 'name': "Bryan Ayala", 'weight': 160, 'height': 70, 'reach': 87.2, 'age': 19, 'fights': 20, 'wins': 3},
        {'id': 3, 'name': "Mark Cuban", 'weight': 200, 'height': 74, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 2}    
    ]
    
    lb = get_leaderboard()
    
    expected_result = [
        {'id': 1, 'name': "Sean Zhang", 'weight': 175, 'height': 71, 'reach': 87.2, 'age': 19, 'fights': 10, 'wins': 6},
        {'id': 4, 'name': "Peter Griffin", 'weight': 400, 'height': 75, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 4},
        {'id': 2, 'name': "Bryan Ayala", 'weight': 160, 'height': 70, 'reach': 87.2, 'age': 19, 'fights': 20, 'wins': 3},
        {'id': 3, 'name': "Mark Cuban", 'weight': 200, 'height': 74, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 2}    
    ]
    
    assert lb == expected_result, f"Expected {expected_result}, but got {lb}"
    
    expected_query = normalize_whitespace("""
            SELECT id, name, weight, height, reach, age, fights, wins,
                (wins * 1.0 / fights) AS win_pct
            FROM boxers
            WHERE fights > 0
        """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
def test_get_leaderboard_by_winpct(mock_cursor):
    """ Testing the get_leaderboard function using the wins_pct parameter
    """
    mock_cursor.fetchall.return_value = [
        {'id': 4, 'name': "Peter Griffin", 'weight': 400, 'height': 75, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 4},
        {'id': 1, 'name': "Sean Zhang", 'weight': 175, 'height': 71, 'reach': 87.2, 'age': 19, 'fights': 10, 'wins': 6},
        {'id': 3, 'name': "Mark Cuban", 'weight': 200, 'height': 74, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 2},
        {'id': 2, 'name': "Bryan Ayala", 'weight': 160, 'height': 70, 'reach': 87.2, 'age': 19, 'fights': 20, 'wins': 3},
    ]
    
    lb = get_leaderboard("win_pct")
    
    expected_result = [
        {'id': 4, 'name': "Peter Griffin", 'weight': 400, 'height': 75, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 4},
        {'id': 1, 'name': "Sean Zhang", 'weight': 175, 'height': 71, 'reach': 87.2, 'age': 19, 'fights': 10, 'wins': 6},
        {'id': 3, 'name': "Mark Cuban", 'weight': 200, 'height': 74, 'reach': 87.2, 'age': 40, 'fights': 5, 'wins': 2},
        {'id': 2, 'name': "Bryan Ayala", 'weight': 160, 'height': 70, 'reach': 87.2, 'age': 19, 'fights': 20, 'wins': 3},
    ]
    
    assert lb == expected_result, f"Expected {expected_result}, but got {lb}"
    
    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
            (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
def test_get_leaderboard_bad_sortby_parameter():
    """ Testing the get_leaderboard function using an invalid sort_by parameter 
    (should raise error)
    """
    with pytest.raises(ValueError, match=r"Invalid sort_by parameter: age"):
        get_leaderboard(sort_by = "age")

######################################################
#
#    Get Boxer
#
######################################################

def test_get_boxer_by_id(mock_cursor):
    """ Testing the get_boxer_by_id function
    """
    mock_cursor.fetchone.return_value = (1, "Sean Zhang", 175, 71, 87.2, 18)
    
    actual_result = get_boxer_by_id(1)
    expected_result = Boxer(1, "Sean Zhang", 175, 71, 87.2, 18)
    
    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"
    
    expected_query = normalize_whitespace("""
                    SELECT id, name, weight, height, reach, age
                    FROM boxers WHERE id = ?
                """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_boxer_by_bad_id(mock_cursor):
    """ Testing the get_boxer_by_id function with an id belonging to no boxer 
    (should raise an error)
    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match=r"Boxer with ID 999 not found"):
        get_boxer_by_id(999)

def test_get_boxer_by_name(mock_cursor):
    """ Testing the get_boxer_by_name function
    """
    mock_cursor.fetchone.return_value = (1, "Sean Zhang", 175, 71, 87.2, 18)
    
    actual_result = get_boxer_by_name("Sean Zhang")
    expected_result = Boxer(1, "Sean Zhang", 175, 71, 87.2, 18)
    
    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"
    
    expected_query = normalize_whitespace("""
                    SELECT id, name, weight, height, reach, age
                    FROM boxers WHERE name = ?
                """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Sean Zhang",)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_boxer_by_bad_name(mock_cursor):
    """ Testing the get_boxer_by_name function with a name belonging to no boxer 
    (should raise an error)
    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match=r"Boxer 'Sean Zhang' not found\."):
        get_boxer_by_name("Sean Zhang")

def test_get_weight_class():
    """ Testing the get_weight_class function
    """
    weights = [203,167,165,125]
    actual_result = []
    
    for weight in weights:
        wclass = get_weight_class(weight)
        actual_result.append(wclass)
        
    expected_result = ['HEAVYWEIGHT','MIDDLEWEIGHT','LIGHTWEIGHT','FEATHERWEIGHT']
    
    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"
    
def test_get_weight_class_bad():
    """ Testing the get_weight_class function with a weight < 125
    """
    with pytest.raises(ValueError, match=r"Invalid weight: 124\. Weight must be at least 125\."):
        get_weight_class(124)

######################################################
#
#    Update stats
#
######################################################

def test_update_boxer_stats(mock_cursor):
    """ Testing the update_boxer_stats function
    """
    mock_cursor.fetchone.return_value = True
    
    boxer_id = 1
    update_boxer_stats(boxer_id, 'win')
    
    
    expected_query = normalize_whitespace("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    
def test_update_boxer_stats_bad(mock_cursor):
    """ Testing the update_boxer_stats function with a result that is not 'win' or 'loss'
    (should raise error)
    """
    mock_cursor.fetchone.return_value = True
    
    boxer_id = 1
    with pytest.raises(ValueError, match=r"Invalid result: W\. Expected 'win' or 'loss'\."):
        update_boxer_stats(boxer_id, 'W')
    
    