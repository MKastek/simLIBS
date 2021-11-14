# Simulated LIBS

Project created for **B.Eng. thesis**:  
Computer methods of the identification of the elements in optical spectra obtained by Laser Induced Breakdown Spectroscopy.

**Thesis supervisor**: Paweł Gąsior PhD  
e-mail: pawel.gasior@ifpilm.pl  
Institute of Plasma Physics and Laser Microfusion

*SimulatedLIBS* provides simple Python class to simulate LIBS spectra with NIST LIBS Database interface.

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
```python
libs = simulation.SimulatedLIBS(Te=1.0, Ne=10**17, elements=['W','H','Be'],percentages=[50,25,25],
                                resolution=1000,low_w=200,upper_w=1000,max_ion_charge=3)
```

### Plot
```python
libs.plot(color='blue', title='W Be H composition')
```

### Save to file
```python
libs.save_to_csv('filename.csv')
```

### Interpolated intensity
SimulatedLIBS interpolates retrieved data from NIST with cubic splines
```python
libs.get_interpolated_intensity()
```
