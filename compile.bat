@echo off
call "C:\OSGeo4W\bin\o4w_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc
pip install --upgrade pip
pip install "dist/Fiona-1.8.20-cp39-cp39-win_amd64.whl"
pip install rtree
pip install geopandas
pip install pandas
pip install geopy
