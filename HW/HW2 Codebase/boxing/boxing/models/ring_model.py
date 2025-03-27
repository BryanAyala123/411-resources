import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class that simulates a fight between two boxers

    Attributes:
        List[Boxer] = contains the two boxers inside of the ring
    """
    def __init__(self):
        """Initializes the RingModel class with an empty ring
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Function that simulates the actual fight between the two boxers in the Ring.
        Utilizes the difference in fighting skill between boxers to get simulate a result.
        After function is called and the winner is determined, the ring clears itself.
        Raises:
            ValueError: If there are less than 2 boxers in the ring.

        Returns:
            winner.name (str): Winning Boxer.
        """
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """Function used to clear the list ring.

        Returns:
            An empty list in self.ring
        """
        logger.info(f"Rquest to empty the list ring")
        if not self.ring:
            return
        self.ring.clear()
        logger.info(f"Successfully emptied the ring")

    def enter_ring(self, boxer: Boxer):
        """
        Adds a Boxer to the ring. GETTT READY TO RUMBLE!

        Args:
            boxer (Boxer): An instance of the Boxer class

        Raises:
            TypeError: If inputted boxer is not of a Boxer class.
            ValueError: If the ring (list[Boxer]) already has 2 boxers inside.
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Give the two boxer inside the ring

        Returns:
            A list containing the boxers inside the ring
        """
        logger.info(f"Request to get the two boxers in the ring")
        if not self.ring:
            pass
        else:
            pass
        logger.info(f"Successfully got the boxers from the ring")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Computes the fighting skill of a unique boxer

        Args:
            boxer(Boxer): The boxer that is in the database

        Returns:
            skill (int) = skill determined by boxer weight times the lenght of the boxers name plus the boxer reach
        divided by 10 and plus an age modifier
        """
        logger.info(f"Request to get fighting skill of boxer")
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.info(f"Successfully returned fighting skill of {skill}")
        return skill
