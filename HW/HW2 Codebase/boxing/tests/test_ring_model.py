from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for resting purposes."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1,"Henry", 138, 43, 20, 30)

@pytest.fixture
def sample_boxer2():
    return Boxer(2,"Taylor", 200, 80, 50, 18)

@pytest.fixture
def sample_boxer3():
    return Boxer(3,"Cade", 145, 50, 10, 25)

@pytest.fixture
def sample_ring1(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

@pytest.fixture
def sample_ring2(sample_boxer1):
    return [sample_boxer1]

@pytest.fixture
def sample_ring3():
    return []
####################################################
# Add / Remove boxer from ring Management Test Cases
####################################################

def test_enter_ring_empty(ring_model, sample_boxer2):
    """Test adding a boxer to the ring
    """
    ring_model.enter_ring(sample_boxer2)

    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == "Taylor"

def test_ring_max_capacity(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test ring can only hold 2 boxers
    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    with pytest.raises(ValueError, match="Ring already has 2 boxers in the ring"):
        ring_model.enter_ring(sample_boxer3)
    
def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the ring
    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.clear_ring()

    assert len(ring_model.ring) == 0, "Playlist should be empty after clearing"

##################################################
# Handleling Fighting
##################################################
    
def test_fight_skill(ring_model, sample_boxer1):
    """Test the fighting skill a boxer
    """
    ring_model.get_fighting_skill(sample_boxer1)

    assert ring_model.get_fighting_skill(sample_boxer1) ==  (138 * len("Henry")) + (20 / 10) + (-2)

def test_fight_ring(ring_model, sample_boxer1, sample_boxer2):
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    ring_model.fight()
    
    assert len(ring_model.ring) == 0

def test_fight_ring_one_boxer(ring_model, sample_boxer1):
    ring_model.enter_ring(sample_boxer1)

    with pytest.raises(ValueError, match="Need to have at least 2 boxers in the ring"):
        ring_model.fight()