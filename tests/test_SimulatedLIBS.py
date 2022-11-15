from SimulatedLIBS.simulation import SimulatedLIBS


def test_static():
    libs = SimulatedLIBS(elements=["H"], percentages=[100], webscraping="static")
    assert libs.get_raw_spectrum() is not None
    assert libs.get_interpolated_spectrum() is not None


def test_dynamic():
    libs = SimulatedLIBS(elements=["H"], percentages=[100], webscraping="dynamic")
    assert libs.get_raw_spectrum() is not None
    assert libs.get_interpolated_spectrum() is not None
