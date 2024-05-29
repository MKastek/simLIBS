import sys
from typing import List

from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import random
import os
from scipy.interpolate import CubicSpline
from concurrent.futures import ThreadPoolExecutor
import math
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import urllib3

urllib3.disable_warnings()


class CompositionError(Exception):
    pass


def validate_simulated_libs(
    Te: float,
    Ne: float,
    elements: List[str],
    percentages: List[float],
    low_w: int,
    upper_w: int,
    max_ion_charge: int,
):
    """
    Validates the input parameters for SimulatedLIBS.

    Raises:
        CompositionError: If the sum of percentages exceeds 100.
        ValueError: If any parameter has an invalid value (negative, wrong order).
    """
    if sum(percentages) > 100:
        raise CompositionError("Sum of element percentages cannot exceed 100%")
    if (
        any(value < 0 for value in [Te, Ne, max_ion_charge])
        or low_w > upper_w
        or len(elements) != len(percentages)
    ):
        raise ValueError(
            "Invalid parameters: negative values, wrong wavelength order, or element/percentage mismatch."
        )


class SimulatedLIBS(object):

    def __init__(
        self,
        Te: float = 1.0,
        Ne: float = 10**17,
        elements: list[str] = None,
        percentages: list[float] = None,
        resolution: int = 1000,
        low_w: int = 200,
        upper_w: int = 1000,
        max_ion_charge: int = 3,
        webscraping: str = "static",
    ):
        """

        Parameters
        ----------
        Te : float
             Electron temperature Te [eV]
        Ne: float
            Electron density Ne [cm^-3]
        elements: list[str]
            List of elements
        percentages: list[percentages]
            List of element percentages
        resolution: int
            Resoultion of spectrometer
        low_w: int
            Lower wavelength [nm]
        upper_w: int
            Upper wavelength [nm]
        max_ion_charge: int
            Maximal ion charge
        webscraping : str
            Type of webscraping: 'static' or 'dynamic'

        """

        validate_simulated_libs(
            Te, Ne, elements, percentages, low_w, upper_w, max_ion_charge
        )

        self.Te = Te
        self.Ne = round(Ne, 3 - int(math.floor(math.log10(abs(Ne)))) - 1)
        self.Ne = re.sub(r"\+", "", str(self.Ne))

        self.elements = elements
        self.percentages = percentages
        self.resolution = resolution
        self.low_w = low_w
        self.upper_w = upper_w
        self.max_ion_charge = max_ion_charge

        self.raw_spectrum = pd.DataFrame({"wavelength": [], "intensity": []})
        self.interpolated_spectrum = pd.DataFrame({"wavelength": [], "intensity": []})
        self.webscraping = webscraping

        match webscraping:
            case "static":
                self.retrieve_data_static()
                self.interpolate()
            case "dynamic":
                self.ion_spectra = None
                options = Options()
                options.add_argument("--disable-notifications")
                options.headless = True

                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.retrieve_data_dynamic()
                self.driver.quit()
                self.driver.stop_client()

    def __repr__(self):
        return f"SimulatedLIBS(Te={self.Te:.2f} eV, Ne={self.Ne:.3e} cm^-3, elements={', '.join(self.elements)}, percentages={', '.join([str(p) for p in self.percentages])}, resolution={self.resolution}, low_w={self.low_w}, upper_w={self.upper_w}, max_ion_charge={self.max_ion_charge})"

    def __str__(self):
        return f"Te: {self.Te:.2f} eV, Ne: {self.Ne:.3e} cm^-3, elements: {', '.join(self.elements)}, percentages: {', '.join([str(p) for p in self.percentages])}"

    def get_site(self):
        """

        Returns
        -------

        """
        composition = ""
        spectrum = ""

        for i in range(len(self.elements)):
            if i > 0:
                composition += "3B"
                spectrum += "2C"
            composition += str(self.elements[i])
            composition += "%3A"
            composition += str(self.percentages[i])

            spectrum += str(self.elements[i])
            spectrum += "0-" + str(self.max_ion_charge)

            if i < len(self.elements) - 1:
                composition += "%"
                spectrum += "%"
        site = (
            "https://physics.nist.gov/cgi-bin/ASD/lines1.pl?composition={}"
            "&spectra={}"
            "&low_w={}&limits_type=0&upp_w={}"
            "&show_av=3&unit=1"
            "&resolution={}"
            "&temp={}"
            "&eden={}"
            "&maxcharge={}"
            "&min_rel_int=0.01"
            "&int_scale=1"
            "&libs=1"
        )
        site = site.format(
            composition,
            spectrum,
            self.low_w,
            self.upper_w,
            self.resolution,
            self.Te,
            self.Ne,
            self.max_ion_charge,
        )

        return site

    def retrieve_data_dynamic(self):
        """

        Returns
        -------

        """
        site = self.get_site()
        self.driver.get(site)
        resolution_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div[1]/div[1]/form/div[3]/div/input")
            )
        )
        resolution_input.clear()
        resolution_input.send_keys(str(self.resolution))

        button_recalculate = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div[1]/div[1]/form/button")
            )
        )
        button_recalculate.click()

        button_csv = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div[2]/button[2]")
            )
        )
        button_csv.click()

        self.driver.switch_to.window((self.driver.window_handles[1]))

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.ion_spectra = pd.read_csv(io.StringIO(soup.pre.text), sep=",").fillna(0)
        self.raw_spectrum["wavelength"] = self.ion_spectra["Wavelength (nm)"]
        self.raw_spectrum["intensity"] = self.ion_spectra["Sum(calc)"]

        self.interpolated_spectrum["wavelength"] = self.ion_spectra["Wavelength (nm)"]
        self.interpolated_spectrum["intensity"] = self.ion_spectra["Sum(calc)"]

    def retrieve_data_static(self):
        """

        Returns
        -------

        """
        site = self.get_site()
        respond = requests.get(site, verify=False)
        soup = BeautifulSoup(respond.content, "html.parser")
        html_data = soup.find_all("script")
        html_data = list(filter(lambda t: "var dataDopplerArray" in str(t), html_data))
        self.retrieve_spectrum_from_html(str(html_data[0]))

    def retrieve_spectrum_from_html(self, html_data: str):

        start_index_of_spectrum_data = [
            (m.start(0), m.end(0))
            for m in re.finditer(r"var dataDopplerArray=.*", html_data)
        ]
        stop_index_of_spectrum_data = [
            (m.start(0), m.end(0))
            for m in re.finditer(r"]];\n    var dataSticksArray.*", html_data)
        ]
        spectrum_data = html_data[
            start_index_of_spectrum_data[0][1]
            + 1 : stop_index_of_spectrum_data[0][0]
            + 1
        ].split(",\n")
        i = 0
        for spectrums in spectrum_data:
            spectrum = spectrums[1:-1].split(",")
            self.raw_spectrum.loc[i] = [spectrum[0], spectrum[1]]
            i += 1

    def interpolate(self, resolution: float = 0.1):
        """
        interpolation of intensity with given resolution using CubicSpline
        """
        cs = CubicSpline(
            self.raw_spectrum["wavelength"],
            self.raw_spectrum["intensity"],
            bc_type="natural",
        )
        x = np.arange(self.low_w, self.upper_w, resolution)
        y = np.clip(cs(x), 0, np.inf)

        self.interpolated_spectrum["wavelength"] = np.round(x, 3)
        self.interpolated_spectrum["intensity"] = np.round(y, 3)

    def plot(
        self,
        color=(random.random(), random.random(), random.random()),
        title="Simulated LIBS",
    ):
        plt.plot(
            self.interpolated_spectrum["wavelength"],
            self.interpolated_spectrum["intensity"],
            label=str(self.elements) + str(self.percentages),
            color=color,
        )
        plt.grid()
        plt.title(title)
        plt.xlabel(r"$\lambda$ [nm]")
        plt.ylabel("Line Intensity [a.u.]")

    def plot_ion_spectra(self):

        self.ion_spectra.drop(["Sum(calc)"], axis=1).plot(
            x="Wavelength (nm)",
            xlabel=r"$\lambda$ [nm]",
            ylabel="Line Intensity [a.u.]",
            title="Ion spectra",
            grid=True,
        )

    def get_interpolated_spectrum(self):
        return self.interpolated_spectrum

    def get_raw_spectrum(self):
        return self.raw_spectrum

    def get_ion_spectra(self):

        if self.webscraping == "dynamic" and self.ion_spectra is not None:
            return self.ion_spectra
        else:
            raise ValueError(
                "Data retrieval requires webscraping method set to 'dynamic' and successful data acquisition."
            )

    def save_to_csv(self, filepath: str):
        self.interpolated_spectrum.to_csv(path_or_buf=filepath)

    @staticmethod
    def worker(
        input_df: pd.DataFrame,
        Te_min: float,
        Te_max: float,
        Ne_min: float,
        Ne_max: float,
        webscraping: str,
    ):
        seed = random.randrange(len(input_df))
        percentages = input_df.iloc[seed].values[:-1]
        elements = input_df.iloc[seed].keys().values[:-1]
        name = input_df.iloc[seed]["name"]
        Te = random.uniform(Te_min, Te_max)
        Ne = random.uniform(Ne_min, Ne_max)
        fun = SimulatedLIBS(
            Te=Te,
            Ne=Ne,
            elements=elements,
            percentages=percentages,
            webscraping=webscraping,
        ).get_interpolated_spectrum()

        return {
            "spectrum": fun,
            "composition": pd.DataFrame(
                {"elements": elements, "percentages": percentages}
            ),
            "name": name,
            "Te[eV]": Te,
            "Ne[cm^-3]": Ne,
        }

    @staticmethod
    def create_dataset(
        input_composition_df: pd.DataFrame,
        size: int = 10,
        Te_min: float = 1.0,
        Te_max: float = 2.0,
        Ne_min: float = 10**17,
        Ne_max: float = 10**18,
        webscraping: str = "static",
    ) -> pd.DataFrame:
        """

        Parameters
        ----------
        input_composition_df: pd.DataFrame
            Input df with composition of elements to simulate
        size : int
            Output file size - number of simulated samples
        Te_min : float
            Minimal random electron temperature Te[eV]
        Te_max : float
            Maximal random electron temperature Te[eV]
        Ne_min : float
            Minimal random electron density Ne[cm^-3]
        Ne_max : float
            Maximal random electron density Ne[cm^-3]
        webscraping : str
            Webscraping type 'static' or 'dynamic'

        Returns
        -------

        """
        pool = ThreadPoolExecutor(size)
        spectra_pool = [
            pool.submit(
                SimulatedLIBS.worker,
                input_composition_df,
                Te_min,
                Te_max,
                Ne_min,
                Ne_max,
                webscraping,
            )
            for _ in range(size)
        ]
        columns = [
            str(wavelength)
            for wavelength in spectra_pool[0].result()["spectrum"]["wavelength"]
        ]
        for val in input_composition_df.columns.values:
            columns.append(str(val))
        columns.append("Te[eV]")
        columns.append("Ne[cm^-3]".format(Ne_min=Ne_min))
        output_df = pd.DataFrame(columns=columns)

        for spectra in spectra_pool:
            intensity = spectra.result()["spectrum"]["intensity"].values.tolist()

            percentages = spectra.result()["composition"]["percentages"].values.tolist()
            intensity.extend(percentages)
            intensity.append(spectra.result()["name"])
            intensity.append(spectra.result()["Te[eV]"])
            intensity.append(spectra.result()["Ne[cm^-3]".format(Ne_min=Ne_min)])
            output_df = pd.concat(
                [output_df, pd.DataFrame(data=[intensity], columns=columns)],
                ignore_index=True,
            )

        output_df.reset_index(drop=True)
        return output_df
