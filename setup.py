from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["matplotlib>=2.2.2,<3","numpy>=1.16","netCDF4>=1.3","pyhdf>=0.10.1","h5py>=2.7"]

setup(
    name="pyhdf45view",
    version="0.0.5",
    author="Martina M Friedrich",
    author_email="5464@gmx.net",
    description="A package to interactively view netCDF and hdf4/ hdf5 files",
    #long_description=readme,
    #long_description_content_type="text/markdown",
    url="https://github.com/mmf1982/pyhdf45view/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)

