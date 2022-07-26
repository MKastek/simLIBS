# Simulated LIBS

*SimulatedLIBS* provides simple Python class to simulate LIBS spectra with NIST LIBS Database interface.

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
libs = simulation.SimulatedLIBS(Te=1.0, Ne=10**17, elements=['W','H','Be'],percentages=[50,25,25],
                                resolution=1000,low_w=200,upper_w=1000,max_ion_charge=3, webscraping='static')
```

### Plot
```python
libs.plot(color='blue', title='W Be H composition')
```
![](images/plot_static.png)

### Save to file
```python
libs.save_to_csv('filename.csv')
```

### Interpolated spectrum
SimulatedLIBS interpolates retrieved data from NIST with cubic splines
```python
libs.get_interpolated_spectrum()
```

### Raw spectrum
Raw retrieved data from NIST
```python
libs.get_raw_spectrum()
```
### Dynamic websraping
```python
libs = simulation.SimulatedLIBS(Te=1.0, Ne=10**17, elements=['W','H','Be'],percentages=[50,25,25],
                                resolution=1000,low_w=200,upper_w=1000,max_ion_charge=3, webscraping='dynamic')
```

### Plot
```python
libs.plot(color='blue', title='W Be H composition')
```
![](images/plot_dynamic.png)

### Random dataset of samples
Based on .csv file with chemical composition of samples, one can generate dataset of simulated LIBS measurements  
with different Te and Ne values

Example of input .csv file:

|W  |H  |He |name|
|---|---|---|----|
|50 |25 |25 |A   |
|30 |60 |10 |B   |
|40 |40 |20 |C   |

```python
if __name__ == '__main__':
    simulation.SimulatedLIBS.create_dataset(input_csv_file="data.csv", output_csv_file='output.csv', size=100, Te_min=1.0, Te_max=2.0, Ne_min=10**17, Ne_max=10**18)
```



