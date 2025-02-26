import simulator.main_loop as mp

def test_instance_create():
    instance1 = mp.Simulator()
    instance2 = mp.get_simulator_instance()
    assert instance1 is instance2