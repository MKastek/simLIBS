import numpy as np
import pandas as pd
import pytest

import os
from simLIBS import validate_simulated_libs, SimulatedLIBS
from simLIBS.simulation import CompositionError


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
    input_df = pd.read_csv("data.csv")
    libs_df = SimulatedLIBS.create_dataset(input_df, size=1)
    assert (
        input_df[
            input_df["name"] == libs_df.iloc[:, -6:-2]["name"].iloc[0]
        ].values.tolist()[0]
        == libs_df.iloc[:, -6:-2].iloc[0].values.tolist()
    )
    assert libs_df.iloc[:, :-6].max().max() > 0
    if os.path.exists("out_put.csv"):
        os.remove("out_put.csv")


def test_valid_parameters():
    # Test with valid parameters
    valid_elements = ["H", "He"]
    valid_percentages = [50, 50]
    validate_simulated_libs(1.0, 1e17, valid_elements, valid_percentages, 200, 1000, 3)


def test_invalid_composition_sum():
    # Test with composition sum exceeding 100%
    elements = ["H", "He"]
    percentages = [60, 50]
    with pytest.raises(CompositionError) as excinfo:
        validate_simulated_libs(1.0, 1e17, elements, percentages, 200, 1000, 3)
    assert str(excinfo.value) == "Sum of element percentages cannot exceed 100%"


def test_negative_parameters():
    # Test with negative values for Te, Ne, or max_ion_charge
    elements = ["H"]
    percentages = [100]
    with pytest.raises(ValueError) as excinfo:
        validate_simulated_libs(-1.0, 1e17, elements, percentages, 200, 1000, 3)
    assert "Invalid parameters" in str(excinfo.value)


def test_invalid_wavelength_order():
    # Test with lower wavelength greater than upper wavelength
    elements = ["H"]
    percentages = [100]
    with pytest.raises(ValueError) as excinfo:
        validate_simulated_libs(1.0, 1e17, elements, percentages, 1000, 200, 3)
    assert "Invalid parameters" in str(excinfo.value)


def test_unequal_element_percentage_length():
    # Test with different lengths of elements and percentages lists
    elements = ["H", "He"]
    percentages = [50]
    with pytest.raises(ValueError) as excinfo:
        validate_simulated_libs(1.0, 1e17, elements, percentages, 200, 1000, 3)
    assert "Invalid parameters" in str(excinfo.value)
