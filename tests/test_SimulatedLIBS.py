from SimulatedLIBS.simulation import SimulatedLIBS


def test():
    libs = SimulatedLIBS(elements=["H"], percentages=[100])
    assert libs.get_raw_spectrum() is not None
