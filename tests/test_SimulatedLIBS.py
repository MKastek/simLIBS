import numpy as np
from SimulatedLIBS.simulation import SimulatedLIBS
import os


def test_static():
    libs = SimulatedLIBS(elements=["H"], percentages=[100], webscraping="static")
    assert libs.get_raw_spectrum() is not None
    assert libs.get_interpolated_spectrum() is not None


def test_values():
    intensity_values = [
        264900.00,
        683500.00,
        1071000.00,
        1019000.00,
        588500.00,
        206500.00,
        43980.00,
        5689.00,
        446.90,
        21.32,
    ]
    libs = SimulatedLIBS(
        elements=["He", "W"], percentages=[50, 50], webscraping="static"
    )
    assert np.allclose(intensity_values, libs.interpolated_spectrum[:10]["intensity"])


def test_dataset():
    libs_df = SimulatedLIBS.create_dataset(input_csv_file="data.csv", size=1)
    assert libs_df.iloc[:, :-6].max().max() > 0
    if os.path.exists("out_put.csv"):
        os.remove("out_put.csv")
