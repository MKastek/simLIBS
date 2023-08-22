# Simulated LIBS

[![PyPI version](https://img.shields.io/pypi/v/SimulatedLIBS?style=flat&logo=pypi)](https://pypi.org/project/SimulatedLIBS/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE.md)
![Tests](https://github.com/MKastek/SimulatedLIBS/actions/workflows/test.yml/badge.svg)
[![ZENADO DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7260706.svg)](https://doi.org/10.5281/zenodo.7260706)

*SimulatedLIBS* provides Python class to simulate LIBS spectra with NIST LIBS Database interface.
*SimulatedLIBS* also allows the creation of simulated data sets that can be used to train ML models.
*SimulatedLIBS* was mentioned is [FOSS For Spectroscopy](https://bryanhanson.github.io/FOSS4Spectroscopy/) by Prof. Bryan A. Hanson, DePauw University.

Project created for **B.Eng. thesis**:
Computer methods of the identification of the elements in optical spectra obtained by Laser Induced Breakdown Spectroscopy.

**Thesis supervisor**: Paweł Gąsior PhD
e-mail: pawel.gasior@ifpilm.pl
Institute of Plasma Physics and Laser Microfusion - IPPLM


## Installation
```python
pip install SimulatedLIBS
```
## Import

```python
from SimulatedLIBS import simulation
```
## Example
Parameters:
- Te - electron temperature [eV]
- Ne - electron density [cm^-3]
- elements - list of elements
- percentages - list of elements concentrations
- resoulution
- wavelength range: low_w, upper_w
- maximal ion charge: max_ion_charge
- websraping: 'static' or 'dynamic'


### Static websraping
```python
libs = simulation.SimulatedLIBS(Te=1.0,
                                Ne=10**17,
                                elements=['W','Fe','Mo'],
                                percentages=[50,25,25],
                                resolution=1000,
                                low_w=200,
                                upper_w=1000,
                                max_ion_charge=3,
                                webscraping='static')
```

### Plot
```python
libs.plot(color='blue', title='W Fe Mo composition')
```
![](https://github.com/MKastek/SimulatedLIBS/blob/master/images/plot_static.png?raw=True)

### Save to file
```python
libs.save_to_csv('filename.csv')
```

### Interpolated spectrum
SimulatedLIBS interpolates retrieved data from NIST with cubic splines.
```python
libs.get_interpolated_spectrum()
```

### Raw spectrum
Raw retrieved data from NIST
```python
libs.get_raw_spectrum()
```
### Dynamic webscraping
```python
libs = simulation.SimulatedLIBS(Te=1.0,
                                Ne=10**17,
                                elements=['W','Fe','Mo'],
                                percentages=[50,25,25],
                                resolution=1000,
                                low_w=200,
                                upper_w=1000,
                                max_ion_charge=3,
                                webscraping='dynamic')
```

### Plot
```python
libs.plot(color='blue', title='W Fe Mo composition')
```
![](https://github.com/MKastek/SimulatedLIBS/blob/master/images/plot_dynamic.png?raw=True)

### Ion spectra
After simulation with parameter websraping = dynamic, ion spectra are stored in ion_spectra (pd.DataFrame) and can be plotted.
```python
libs.plot_ion_spectra()
```
![](https://github.com/MKastek/SimulatedLIBS/blob/master/images/plot_ion_spectra.png?raw=True)
### Random dataset of samples
Based on .csv file with chemical composition of samples, one can generate dataset of simulated LIBS measurements
with different Te and Ne values.

Example of input .csv file:

|W  |H  |He |name|
|---|---|---|----|
|50 |25 |25 |A   |
|30 |60 |10 |B   |
|40 |40 |20 |C   |

```python
simulation.SimulatedLIBS.create_dataset(input_csv_file="data.csv",
                                        output_csv_file='output.csv',
                                        size=100,
                                        Te_min=1.0,
                                        Te_max=2.0,
                                        Ne_min=10**17,
                                        Ne_max=10**18)
```

Example of output .csv file:

|    |   200.0 |   200.1 |   200.2 |   200.3 |   200.4 | ...   |   H |   W |   Te |       Ne |
|---:|--------:|--------:|--------:|--------:|--------:|----:|----:|----:|-----:|---------:|
|  0 |       0 |     0   |     0   |     0   |     0   | ...   |2 |   50 | 1.43 | 1.08e+17 |
|  1 |       0 |     0   |     0   |     0   |     0   | ...   |0 |   0 | 1.06 | 1.08e+17 |
|  2 |       0 |     0.1 |     0.1 |     0.1 |     0.1 | ...   |0 |  68 | 1.82 | 1.18e+17 |
|  3 |       0 |    54.5 |    56.7 |    54.4 |    48.4 | ...   |0 |   3 | 1.25 | 1.06e+17 |
|  4 |       0 |   121.7 |   143.1 |   140.5 |   115.3 | ...   |0 |  84 | 1.08 | 9.23e+17 |


### Animations
SimulatedLIBS can be helpful in creating LIBS animations mostly for educational purpose.

#### Resolution animation
Changes in resolution in range: 500-10000.
![](https://github.com/MKastek/SimulatedLIBS/blob/master/SimulatedLIBS/animations/saved-gifs/animated_resolution.gif?raw=True)
#### Electron temperature animation
Changes in electron temperature Te in range: 0.5-5 eV.
![](https://github.com/MKastek/SimulatedLIBS/blob/master/SimulatedLIBS/animations/saved-gifs/animated_temperature.gif?raw=True)
#### Electron density animation
Changes in electron density Ne in range: 0.7-1.3 e+17 [cm^-3].
![](https://github.com/MKastek/SimulatedLIBS/blob/master/SimulatedLIBS/animations/saved-gifs/animated_density.gif?raw=True)

## References
- M. Kastek, _et al._, _Analysis of hydrogen isotopes retention in thermonuclear reactors with LIBS supported by machine learning_. Spectrochimica Acta Part B Atomic Spectroscopy 199: 106576. DOI: [10.1016/j.sab.2022.106576](https://doi.org/10.1016/j.sab.2022.106576).


## Used in Research
- Chen Z, Chen Z, Jiang W, Guo L, Zhang Y. _Line intensity calculation of laser-induced breakdown spectroscopy during plasma expansion in nonlocal thermodynamic equilibrium._ Opt Lett. 2023 Jun 15;48(12):3227-3230. DOI: [10.1364/OL.488250](https://opg.optica.org/ol/abstract.cfm?uri=ol-48-12-3227).
