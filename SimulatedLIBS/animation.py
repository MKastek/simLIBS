import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import os
from SimulatedLIBS import simulation


def get_intensity(
    resolution_range, Te_range, Ne_range, elements, percentages, low_w=200, upper_w=1000
):
    intensity = []
    wavelength = []

    for resolution, Te, Ne in zip(resolution_range, Te_range, Ne_range):
        libs = simulation.SimulatedLIBS(
            Te=Te,
            Ne=Ne,
            elements=elements,
            percentages=percentages,
            resolution=resolution,
            low_w=low_w,
            upper_w=upper_w,
            max_ion_charge=3,
            webscraping="dynamic",
        )
        spectrum = libs.get_raw_spectrum()
        wavelength.append(spectrum["wavelength"])
        intensity.append(spectrum["intensity"] / spectrum["intensity"].max())

    return wavelength, intensity


def update_plot(
    index, parameter, wavelength_range, intensity_range, parameter_range, unit
):
    plt.clf()
    plt.plot(wavelength_range[index], intensity_range[index])
    plt.xlabel(r"$\lambda$ [nm]")
    plt.ylabel("Line intensity [a.u]")
    plt.grid()
    plt.title(
        "Elements: ['W', 'Fe', 'Mo'] \n"
        + parameter
        + " : "
        + "{:0.3e}".format(parameter_range[index])
        + " "
        + unit
    )


def animate_resolution(elements, percentages):
    resolution_range = np.arange(500, 10000, 200)
    anim_len = len(resolution_range)
    wavelength_range, intensity_range = get_intensity(
        resolution_range=resolution_range,
        Te_range=[1.0] * anim_len,
        Ne_range=[10**17] * anim_len,
        elements=elements,
        percentages=percentages,
        low_w=200,
        upper_w=400,
    )

    fig = plt.figure()
    anim = animation.FuncAnimation(
        fig,
        update_plot,
        frames=anim_len,
        fargs=("Resolution", wavelength_range, intensity_range, resolution_range, " "),
        interval=200,
    )
    anim.save(
        os.path.join("animations", "saved-gifs", "animated_resolution.gif"),
        writer="imagemagick",
    )
    plt.show()


def animate_temperature(elements, percentages):
    Te_range = np.arange(0.5, 5, 0.25)
    anim_len = len(Te_range)
    wavelength_range, intensity_range = get_intensity(
        resolution_range=[5000] * anim_len,
        Te_range=Te_range,
        Ne_range=[10**17] * anim_len,
        elements=elements,
        percentages=percentages,
        low_w=200,
        upper_w=400,
    )

    fig = plt.figure()
    anim = animation.FuncAnimation(
        fig,
        update_plot,
        frames=anim_len,
        fargs=("Temperature", wavelength_range, intensity_range, Te_range, "[eV]"),
        interval=200,
    )
    anim.save(
        os.path.join("animations", "saved-gifs", "animated_temperature.gif"),
        writer="imagemagick",
    )
    plt.show()


def animate_density(elements, percentages):
    Ne_range = np.arange(0.7, 1.3, 0.05)
    Ne_range *= 10**17
    anim_len = len(Ne_range)
    wavelength_range, intensity_range = get_intensity(
        resolution_range=[5000] * anim_len,
        Te_range=[1.0] * anim_len,
        Ne_range=Ne_range,
        elements=elements,
        percentages=percentages,
        low_w=200,
        upper_w=400,
    )

    fig = plt.figure()
    anim = animation.FuncAnimation(
        fig,
        update_plot,
        frames=anim_len,
        fargs=("Density", wavelength_range, intensity_range, Ne_range, "[$cm^{-3}$]"),
        interval=200,
    )
    anim.save(
        os.path.join("animations", "saved-gifs", "animated_density.gif"),
        writer="imagemagick",
    )
    plt.show()


if __name__ == "__main__":
    animate_density(elements=["W", "Fe", "Mo"], percentages=[50, 25, 25])
    animate_resolution(elements=["W", "Fe", "Mo"], percentages=[50, 25, 25])
    animate_temperature(elements=["W", "Fe", "Mo"], percentages=[50, 25, 25])
