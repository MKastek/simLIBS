import sys

from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import os
from scipy.interpolate import CubicSpline
from concurrent.futures import ProcessPoolExecutor
import time


class MyError(Exception):
    pass


class SimulatedLIBS(object):

    # filepath to class root folder
    project_root = os.path.dirname(os.path.abspath(__file__))

    def __init__(self,Te=1.0,Ne=10**17,elements=None,percentages=None,resolution = 1000,low_w = 200,upper_w = 1000 ,max_ion_charge = 3):

        """
        :param Te:  Electron temperature Te [eV]
        :param Ne:  Electron density Ne [cm^-3]
        :param elements:
        :param percentages: List of element percentages
        :param resolution:
        :param low_w:   Lower wavelength [nm]
        :param upper_w: Upper wavelength [nm]
        :param max_ion_charge:  Maximal ion charge
        """

        if sum(percentages) > 100 or Te < 0 or Ne < 0 or low_w > upper_w or upper_w < low_w or max_ion_charge < 0:
            try:
                raise (MyError("Error in SimulatedLLIBS"))
            except MyError as error:
                print(str(error))
                sys.exit(1)

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
        interpolation of intensity with given resolution using CubicSpline
        """
        cs = CubicSpline(self.raw_spectrum['wavelength'], self.raw_spectrum['intensity'], bc_type='natural')
        x = np.arange(self.low_w, self.upper_w, resolution)
        y = cs(x)
        # none negative values
        y = [0 if i < 0 else i for i in y]

        self.interpolated_spectrum['wavelength'] = np.round(x, 1)
        self.interpolated_spectrum['intensity'] = np.round(y, 1)

    def plot(self,color=(random.random(), random.random(), random.random()),title='Simulated LIBS'):

        # plot with random colors
        plt.plot(self.interpolated_spectrum["wavelength"],self.interpolated_spectrum["intensity"],
                 label=str(self.elements)+str(self.percentages),
                 color=color)
        plt.grid()
        plt.title(title)
        plt.xlabel(r'$\lambda$ [nm]')
        plt.ylabel('Line Intensity [a.u.]')

    def get_interpolated_spectrum(self):
        """
        :return:  interpolated spectrum
        """
        return self.interpolated_spectrum

    def get_raw_spectrum(self):
        """
        :return:  raw spectrum
        """
        return self.raw_spectrum

    def save_to_csv(self,filepath):
        """
        :param filepath:
        :return:
        """
        self.interpolated_spectrum.to_csv(path_or_buf=filepath)

    @staticmethod
    def worker(input_df, num_of_materials,Te_min, Te_max, Ne_min, Ne_max):
        percentages = input_df.iloc[random.randrange(num_of_materials)].values[:-1]
        elements = input_df.iloc[random.randrange(num_of_materials)].keys().values[:-1]
        name = input_df.iloc[random.randrange(num_of_materials)]['name']
        Te = random.uniform(Te_min, Te_max)
        Ne = random.uniform(1, 10)
        fun = SimulatedLIBS(Te=Te,Ne=Ne,elements=elements, percentages=percentages).get_interpolated_spectrum()
        return { 'spectrum': fun, 'composition': pd.DataFrame({'elements':elements, 'percentages': percentages}), 'name': name, 'Te': Te, 'Ne': Ne}

    @staticmethod
    def create_dataset(input_csv_file, output_csv_file='out_put.csv', size=10, Te_min=1.0, Te_max=2.0, Ne_min=10**17, Ne_max=10**18):
        input_df = pd.read_csv(input_csv_file)
        num_of_materials = len(input_df)
        pool = ProcessPoolExecutor(4)
        pp = [pool.submit(SimulatedLIBS.worker,input_df,num_of_materials,Te_min,Te_max,Ne_min,Ne_max) for i in range(size)]
        columns = [str(wavelength) for wavelength in pp[0].result()['spectrum']['wavelength']]
        for val in input_df.columns.values:
            columns.append(str(val))
        columns.append('Te')
        columns.append('Ne')
        output_df = pd.DataFrame(columns=columns)

        for p in pp:
            intensity = p.result()['spectrum']['intensity'].values.tolist()
            percentages = p.result()['composition']['percentages'].values.tolist()
            intensity.extend(percentages)
            intensity.extend(p.result()['name'])
            intensity.append(p.result()['Te'])
            intensity.append(p.result()['Ne'])
            output_df = pd.concat([output_df,pd.DataFrame(data=[intensity],columns=columns)],ignore_index=True)
        output_df.reset_index(drop=True)
        print(output_df)
        output_df.to_csv(output_csv_file)


    @staticmethod
    def create_random_dataset(elements_list,Te_min, Te_max, Ne_min, Ne_max):
        pass


if __name__ == '__main__':
    SimulatedLIBS.create_dataset(input_csv_file=r"C:\Users\marci\Desktop\Python\SimulatedLIBS\data.csv")