from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import os
from scipy.interpolate import CubicSpline



class MyError(Exception):
    pass

__author__ = 'Marcin Katek'


class SimulatedLIBS(object):

    # filepath to class root folder
    project_root = os.path.dirname(os.path.abspath(__file__))

    def __init__(self,Te,Ne,elements,percentages,resolution,low_w,upper_w,max_ion_charge):

        """
        :param Te:  Electron temperature Te [eV]
        :param Ne:  Electron density Ne [cm^-3]
        :param elements:    List of elements_IFPiLM_Te=1_Ne=1e17
        :param percentages: List of element percentages
        :param resolution:
        :param low_w:   Lower wavelength [nm]
        :param upper_w: Upper wavelength [nm]
        :param max_ion_charge:  Maximal ion charge
        """

        """
        if sum(percentages) > 100 or Te < 0 or Ne < 0 or low_w > upper_w or upper_w < low_w or max_ion_charge < 0:
            try:
                raise (MyError("Error in SimulatedLibs"))
            except MyError as error:
                print(str(error))
                sys.exit(1)
        """

        self.Te = Te
        self.Ne = Ne
        self.elements = elements
        self.percentages = percentages
        self.resolution = resolution
        self.low_w = low_w
        self.upper_w = upper_w
        self.max_ion_charge = max_ion_charge

        self.raw_spectrum = pd.DataFrame({"wavelength": [], "intensity": []})
        self.interpolated_spectrum = pd.DataFrame({"wavelength": [], "intensity": []})

        # retrieving data
        self.retrieve_data()
        # interpolating data
        self.interpolate()

    def retrieve_data(self):

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

            if i < len(self.elements)-1:
                composition += "%"
                spectrum += "%"
        site = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl?composition={}" \
               "&spectra={}" \
               "&low_w={}&limits_type=0&upp_w={}" \
               "&show_av=3&unit=1" \
               "&resolution={}" \
               "&temp={}" \
               "&eden={}" \
               "&maxcharge={}" \
               "&min_rel_int=0.01" \
               "&libs=1"
        site = site.format(composition,spectrum,self.low_w,self.upper_w,self.resolution,self.Te,self.Ne,self.max_ion_charge)
        respond = requests.get(site)
        soup = BeautifulSoup(respond.content, 'html.parser')
        html_data = soup.find_all("script")
        html_data = str(html_data[5])

        self.retrieve_spectrum_from_html(html_data)

    def retrieve_spectrum_from_html(self,html_data):
        start_index_of_spectrum_data = [(m.start(0), m.end(0)) for m in re.finditer(r"var dataDopplerArray=.*", html_data)]
        stop_index_of_spectrum_data = [(m.start(0), m.end(0)) for m in re.finditer(r"]];\n    var dataSticksArray.*", html_data)]
        spectrum_data = html_data[start_index_of_spectrum_data[0][1] + 1:stop_index_of_spectrum_data[0][0] + 1].split(",\n")
        i = 0
        for spectrums in spectrum_data:
            spectrum = spectrums[1:-1].split(",")
            self.raw_spectrum.loc[i]= [spectrum[0],spectrum[1]]
            i += 1

    def interpolate(self, resolution=0.1):
        """
        interpolation of intensity with given resolution using CubicSpline,
        with assumption of none negative values and zero values at the ends
        """
        cs = CubicSpline(self.raw_spectrum['wavelength'], self.raw_spectrum['intensity'], bc_type='natural')
        x = np.arange(self.low_w, self.upper_w, resolution)
        y = cs(x)
        # none negative values
        y = [0 if i < 0 else i for i in y]
        # zero values at the ends
        y[0] = 0
        y[-1] = 0

        self.interpolated_spectrum['wavelength'] = np.round(x, 1)
        self.interpolated_spectrum['intensity'] = np.round(y, 1)

    def plot(self,color=(random.random(), random.random(), random.random())):
        # normalization
        norm = [float(i) / max(self.interpolated_spectrum["intensity"]) for i in self.interpolated_spectrum["intensity"]]

        # plot with random colors
        plt.plot(self.interpolated_spectrum["wavelength"],norm,
                 label=str(self.elements)+str(self.percentages),
                 color=color)
        plt.grid()
        plt.title("Simulated LIBS")
        plt.xlabel(r'$\lambda$ [nm]')
        plt.ylabel('Line Intensity [a.u.]')


    def get_intensity_interpolated(self):
        """
        :return:  interpolated intensity for ML predict method (scikit-learn)
        """
        return np.array(self.interpolated_spectrum['intensity']).reshape(1, -1)

    def save_to_csv(self,filename):
        self.interpolated_spectrum.to_csv(path_or_buf=os.path.join(SimulatedLIBS.project_root,filename))




libs = SimulatedLIBS(Te = 1.0, Ne = 10**17, elements = ["W","He","O"], percentages = [50,25,25],
                     resolution = 1000, low_w = 200, upper_w = 1000, max_ion_charge = 3)
libs.save_to_csv('filename')
libs.plot('blue')
plt.show()
