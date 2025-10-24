"""
Dice module for the Zonk dice game.

This module implements dice rolling functionality and score calculation
for the game, including handling special combinations and scoring rules.
"""

from random import randint


class Dice:
    """Represents a set of dice that can be rolled."""

    def __init__(self, count_dice: int = 6) -> None:
        """
        Initialize the dice set.

        Args:
            count_dice: Number of dice in the set (default: 6)
        """

        self.count_dice: int = count_dice

    def roll(self, count_dice: int | None = None) -> list[int]:
        """
        Roll the dice and return the results.

        Args:
            count_dice: Number of dice to roll. If None, uses the default count.

        Returns:
            List of integers representing dice roll results (1-6)
        """

        if count_dice is None:
            count_dice = self.count_dice
        return [randint(1, 6) for _ in range(count_dice)]


class ScoreCalculator:
    """Handles score calculation for dice combinations."""

    @staticmethod
    def calculate_score(dice: list[int]) -> tuple[int, list[int]]:
        """
        Calculate score for a given set of dice.

        Scoring rules:
        - Special combinations with 6 dice:
          * Straight 1-6: 300 points
          * Three pairs: 75 points
          * Two sets of three: 150 points
        - Three or more of a kind:
          * Three 1's: 100 points, more than three: doubled each time
          * Three of other numbers: number x 10 points, more than three: doubled each time
        - Single 1's and 5's: 10 and 5 points respectively

        Args:
            dice: List of dice values (1-6)

        Returns:
            Tuple of (score, list of dice used in scoring)
        """

        dice = sorted(dice)
        score = 0
        used_dice = []

        # Checking for special combinations of 6 dices
        if len(dice) == 6:
            # 6 diffrent
            if dice == [1, 2, 3, 4, 5, 6]:
                return 300, dice.copy()

            # 3 pairs
            if len(set(dice)) == 3 and all(dice.count(d) == 2 for d in set(dice)):
                return 75, dice.copy()

            # 2 sets
            if len(set(dice)) == 2 and all(dice.count(d) == 3 for d in set(dice)):
                return 150, dice.copy()

        # Сreating a copy of the list to work with it directly
        temp_dice = dice.copy()

        # Counting combinations of identical dices
        for value in range(1, 7):
            count = temp_dice.count(value)
            points: int
            if count >= 3:
                if value == 1:
                    if count == 3:
                        points = 100
                    elif count == 4:
                        points = 200
                    elif count == 5:
                        points = 400
                    elif count == 6:
                        points = 1000
                else:
                    points = value * 10
                    if count == 4:
                        points *= 2
                    elif count == 5:
                        points *= 4
                    elif count == 6:
                        points *= 8

                score += points
                # Removing the used dices
                for _ in range(count):
                    temp_dice.remove(value)
                used_dice.extend([value] * count)

        # counting single 1's and 5's from the remaining dices
        for value in [1, 5]:
            while value in temp_dice:
                if value == 1:
                    score += 10
                else:  # value == 5
                    score += 5
                temp_dice.remove(value)
                used_dice.append(value)

        return score, used_dice
