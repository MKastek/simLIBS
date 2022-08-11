import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='SimulatedLIBS',
    version='0.1.4',
    packages=setuptools.find_packages(),
    url='https://github.com/MKastek/SimulatedLIBS',
    license='MIT license',
    author='Marcin Kastek',
    install_requires=['pandas',
                      'numpy',
                      'matplotlib',
                      'requests',
                      'bs4',
                      'scipy',
                      'selenium',
                      'webdriver-manager'],
    author_email='marcin.kastek.stud@pw.edu.pl',
    description='SimulatedLIBS provides simple Python class to simulate LIBS spectra with NIST LIBS Database interface',
    long_description=long_description,
    long_description_content_type="text/markdown",
)