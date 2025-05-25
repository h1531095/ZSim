import pytest
from zsim.simulator.simulator_class import Simulator


class TestSimulator:
    def test_init_simulator(self):
        sim = Simulator()
        assert isinstance(sim, Simulator)
