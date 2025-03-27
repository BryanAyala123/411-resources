from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """
    A class that stores various informations about a singular boxer
    
    Attributes:
        id (int): Boxer's identification number
        name (str): Name of the Boxer
        weight (int): Weight of the Boxer
        height (int): Height of the Boxer
        reach (int): Maximum reach of the Boxer
        age (int): Age of the Boxer
        Weight_class (str): Weight class the Boxer belongs to
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Initializes the Boxer using the specified weight to find thier weight class
        
        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """ 
    Adds the boxer to the database. 
    
    Args: 
        name (str): Name of the Boxer
        weight (int): Weight of the Boxer
        height (int): Height of the Boxer
        reach (int): Maximum reach of the Boxer
        age (int): Age of the Boxer

    Raises:
        ValueError: If an invalid weight, height, reach or age is given. If boxer with the
        same name already exists in the Database.
    """
    if weight < 125:
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

    except sqlite3.IntegrityError:
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer from the specified database.

    Args:
        boxer_id (int): The unqiue ID of a specific boxer

    Raises:
        ValueError: If boxer ID was not found in database

    """
    logger.info("Received request to delete a boxer")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"The Boxer with the ID {boxer_id} does not exist")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Boxer with ID: {boxer_id} had been deleted")

    except sqlite3.Error as e:
        logger.warning(f"{e} sqlite error was thrown")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Function determines an ordering based on a specified parameter, either wins or
    win percentage. If no parameter is specified, wins is used.
    
    Args:
        sort_by (str): Parameter that determines the metric boxers are ranked and listed by
                       Allowed Parameters are wins and win_pct. Default parameter if None
                       inputted is wins.
        
    Raises:
        ValueError: If invalid sort_by parameter is inputted.
    
    Returns:
        leaderboard (list[Boxer]): List with Boxers in order as sorted by specified 
                                   parameter.
    """
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    '''Example function that searches for a boxer given the ID

    Args:
        boxer_id(int): The unqiue identification of a singular boxer.

    Raises:
        ValueError: Boxer could not be found in the data base given the ID.
    
    Returns:
        A boxer from class boxer contain information such as id, name, weight, height, reach, age.
    '''
    logger.info(f"Retrieving the current box by ID: {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfuly gto the boxer {boxer_id}")
                return boxer
            else:
                logger.error(f"Boxer with ID: {boxer_id} does not exist")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.warning(f"{e} sqlite error was thrown")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Searchs in the database for a Boxer with the given name
    
    Args:
        boxer_name (str): Name to search for
        
    Raise:
        ValueError: If not boxer with the specified name is found.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """Example function get the weight class based on the weight given

    Args:
        weight(int): A number representing the weight

    Raises:
        ValueError: If the weight(int) is below 125

    Returns:
        string: the name of the weight class the weight(int) falls under
    """
    logger.info("Received request to get wieght class")
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"The wieght: {weight} has to be at least 125")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")
    logger.info(f"Successfully got the wieghtclass = {weight_class}")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Updates a boxers starts with either a win or a loss, and increments the number
    fights boxer has participated in.

    Args:
        boxer_id (int): Unique Identification Number for a Boxer
        result (str): 

    Raises:
        ValueError: If inputted result is not 'win' or 'loss', or
                    if no boxer with the specified id is found
        e: If an SQLite error is encountered
    """
    if result not in {'win', 'loss'}:
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
