import matplotlib.pyplot as plt

from SimulatedLIBS import simulation

libs = simulation.SimulatedLIBS(
    Te=1.0,
    Ne=10**17,
    elements=["W", "Fe", "Mo"],
    percentages=[50, 25, 25],
    resolution=1000,
    low_w=200,
    upper_w=1000,
    max_ion_charge=3,
    webscraping="static",
)

libs.plot(color="blue", title="W Fe Mo composition")
plt.savefig("output_data/plot_static.png")

libs = simulation.SimulatedLIBS(
    Te=1.0,
    Ne=10**17,
    elements=["W", "Fe", "Mo"],
    percentages=[50, 25, 25],
    resolution=1000,
    low_w=200,
    upper_w=1000,
    max_ion_charge=3,
    webscraping="dynamic",
)

libs.plot(color="blue", title="W Fe Mo composition")
plt.grid()
plt.savefig("output_data/plot_dynamic.png")

libs.plot_ion_spectra()
plt.savefig("output_data/plot_ion_spectra.png")
