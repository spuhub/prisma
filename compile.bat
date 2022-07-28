@echo off
call "C:\OSGeo4W\bin\o4w_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc

pip install --upgrade pip

pip install wheel
pip install pipwin

pip install numpy==1.20.2
pip install pandas==1.1.3
pip install shapely==1.7
pipwin install gdal
pipwin install fiona
pip install pyproj==3.0.1
pip install six
pip install rtree==0.9.7
pip install geos
pip install descartes
pip install geopandas==0.9.0