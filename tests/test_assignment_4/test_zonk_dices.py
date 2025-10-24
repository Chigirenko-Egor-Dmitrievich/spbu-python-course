"""
Tests for the zonk_dices module.
Focuses on dice rolling behavior and score calculation.
"""

import pytest
from unittest.mock import patch
from project.assignment_4.zonk_dices import Dice, ScoreCalculator


def test_dice_initialization():
    """Test dice initialization with custom count."""
    dice = Dice(5)
    assert dice.count_dice == 5


def test_dice_default_initialization():
    """Test dice initialization with default count."""
    dice = Dice()
    assert dice.count_dice == 6


def test_dice_roll_count():
    """Test that roll returns correct number of dice."""
    dice = Dice(4)
    result = dice.roll()
    assert len(result) == 4


def test_dice_roll_custom_count():
    """Test rolling with custom dice count."""
    dice = Dice(6)
    result = dice.roll(3)
    assert len(result) == 3


def test_dice_roll_values_range():
    """Test that dice values are within valid range (1-6)."""
    dice = Dice(10)  # Roll multiple dice to test range
    result = dice.roll()

    assert all(1 <= value <= 6 for value in result)
    assert len(result) == 10


def test_straight_combination():
    """Test scoring for straight combination (1-2-3-4-5-6)."""
    dice = [1, 2, 3, 4, 5, 6]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 300
    assert used_dice == [1, 2, 3, 4, 5, 6]


def test_three_pairs_combination():
    """Test scoring for three pairs combination."""
    dice = [1, 1, 2, 2, 3, 3]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 75
    assert len(used_dice) == 6


def test_two_sets_combination():
    """Test scoring for two sets of three combination."""
    dice = [2, 2, 2, 5, 5, 5]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 150
    assert len(used_dice) == 6


def test_three_ones():
    """Test scoring for three ones."""
    dice = [1, 1, 1, 2, 3, 4]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 100
    assert used_dice.count(1) == 3


def test_four_ones():
    """Test scoring for four ones."""
    dice = [1, 1, 1, 1, 2, 3]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 200
    assert used_dice.count(1) == 4


def test_three_twos():
    """Test scoring for three twos."""
    dice = [2, 2, 2, 3, 4, 5]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 20  # 2 * 10
    assert used_dice.count(2) == 3


def test_single_ones_and_fives():
    """Test scoring for single ones and fives."""
    dice = [1, 5, 2, 3, 4, 6]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 15  # 10 for 1 + 5 for 5
    assert 1 in used_dice
    assert 5 in used_dice


def test_zonk_roll():
    """Test scoring for roll with no points (zonk)."""
    dice = [2, 3, 4, 6, 2, 3]
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 0
    assert len(used_dice) == 0


def test_complex_combination():
    """Test scoring for complex combination."""
    dice = [1, 1, 1, 5, 5, 2]  # Three 1's + two 5's
    score, used_dice = ScoreCalculator.calculate_score(dice)
    assert score == 100 + 10  # 100 for three 1's + 10 for two 5's


def test_state_change_after_calculation():
    """Test that input list is not modified during calculation."""
    original_dice = [1, 2, 3, 4, 5, 6]
    dice_copy = original_dice.copy()

    score, used_dice = ScoreCalculator.calculate_score(original_dice)

    # Original list should remain unchanged
    assert original_dice == dice_copy
    # But we should get a proper score
    assert score == 300
