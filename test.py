from SimulatedLIBS import simulation
import matplotlib.pyplot as plt
import pandas as pd

libs = simulation.SimulatedLIBS(Te=1.0, Ne=10**17, elements=['W','H','Be','Fe'],percentages=[50,25,10,15],
                                resolution=1000,low_w=200,upper_w=1000,max_ion_charge=3)
libs.plot(color='blue', title='W Be H composition')
plt.show()
print(libs.get_raw_spectrum())
print(libs.get_interpolated_spectrum())
print(pd.read_csv('data.csv'))