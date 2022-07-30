import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from SimulatedLIBS import simulation

def get_intensity():
    resolution_range = np.arange(500, 10000, 200)
    intensity = []
    wavelength = []
    print(resolution_range)
    for resolution in resolution_range:
        libs = simulation.SimulatedLIBS(Te=1.0, Ne=10 ** 17, elements=['W', 'Fe', 'Mo'], percentages=[50, 25, 25],
                             resolution=resolution, low_w=200, upper_w=400, max_ion_charge=3, webscraping='dynamic')
        spectrum = libs.get_raw_spectrum()
        wavelength.append(spectrum['wavelength'])
        intensity.append(spectrum['intensity']/spectrum['intensity'].max())

    return wavelength, intensity, resolution_range


wavelength, intensity, resolution_range = get_intensity()

fig = plt.figure()

def update(i):
    plt.clf()
    plt.plot(wavelength[i], intensity[i])
    plt.xlabel(r"$\lambda$ [nm]")
    plt.ylabel("Line intensity [a.u]")
    plt.title("Resolution: " +str(resolution_range))

anim = animation.FuncAnimation(fig, update, frames = 48, interval = 100)
plt.show()
