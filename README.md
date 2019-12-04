# pyhdfview

## to build dependences:
    pip3 install -r requirements_dev.txt

## install under test environement and use pip3 to install
    python3 -m venv test_environment
    source test_environment/bin/activate
    pip3 install  --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple  pyhdf45view
    python3 -m pyhdf45view.pyhdf45view YOURFILE.nc

This is a tool to view netCDF4, hdf4 and hdf5 files. It has enhanced plotting
possiblities. It consists of two packages: netcdf45view.py and Fastplot.py.
The latter can be imported and used independently for plotting 2-/3-D data in
python.
This package comes also with a comparison tool for netCDF4/ hdf4/ hdf5 files
which compares contents and writes differences to a hdf5 file.

I recomment to install it in an environment first:

### Author: Martina M. Friedrich
### Date: 2014 -- 2019
### Version 0.0.5: Dec.4th 2019
