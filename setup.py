import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='SimulatedLIBS',
    version='0.0.8',
    packages=setuptools.find_packages(),
    url='',
    license='',
    author='Marcin Kastek',
    install_requires=[],
    author_email='marcin.kastek.stud@pw.edu.pl',
    description='LIBS',
    long_description=long_description,
    long_description_content_type="text/markdown",
)