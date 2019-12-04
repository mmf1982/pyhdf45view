# pyhdfview
to build dependences:
    pip3 install -r requirements_dev.txt

to use to view FILE.nc:
    python3 pyhdf45view.py FILE.nc

This is a tool to view netCDF4, hdf4 and hdf5 files. It has enhanced plotting
possiblities. It consists of two packages: netcdf45view.py and Fastplot.py.
The latter can be imported and used independently for plotting 2-/3-D data in
python.
This package comes also with a comparison tool for netCDF4/ hdf4/ hdf5 files
which compares contents and writes differences to a hdf5 file.

Author: Martina M. Friedrich
Date: 2014 -- 2019
