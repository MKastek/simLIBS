import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from SimulatedLIBS import simulation


def get_intensity(resolution_range, Te_range, Ne_range, elements, percentages, low_w=200, upper_w=1000):
    intensity = []
    wavelength = []

    for resolution, Te, Ne in zip(resolution_range, Te_range, Ne_range):
        libs = simulation.SimulatedLIBS(Te=Te, Ne=Ne, elements=elements, percentages=percentages,
                             resolution=resolution, low_w=low_w, upper_w=upper_w, max_ion_charge=3, webscraping='dynamic')
        spectrum = libs.get_raw_spectrum()
        wavelength.append(spectrum['wavelength'])
        intensity.append(spectrum['intensity']/spectrum['intensity'].max())

    return wavelength, intensity, resolution_range, Te_range, Ne_range


wavelength, intensity, resolution_range, Te_range, Ne_range = get_intensity(resolution_range = np.arange(500, 10000, 200), )

fig = plt.figure()

def update_plot(parameter, index, wavelength_range, intensity_range, parameter_range):
    plt.clf()
    plt.plot(wavelength_range[index], intensity_range[index])
    plt.xlabel(r"$\lambda$ [nm]")
    plt.ylabel("Line intensity [a.u]")
    plt.grid()
    plt.title(parameter+" : " +str(parameter_range[index]))

def animate_resolution():

    fig = plt.figure()

def animate_temperature():
    pass

def animate_density():
    pass


anim = animation.FuncAnimation(fig, update, frames = len(resolution_range), interval = 150)
anim.save('animated_resolution.gif', writer='imagemagick')
plt.show()

if __name__ == '__main__':
    animate_resolution()
    animate_temperature()
    animate_resolution()