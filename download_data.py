import zipfile
import os

import pandas as pd
import requests

import numpy as np

import ee
import rasterio

import argparse

# Trigger the authentication flow.
ee.Authenticate()

# Initialize the library.
ee.Initialize(project='cs145-db')


def getSentinalS2SRImage(lon, lat, sze, filename, dateMin='2015-01-01',
                         dateMax='2022-12-31', vmin=0, vmax=3500):
    '''
    download an RGB image from the Sentinal S2 Surface Reflectance satellite, at the given coordinates

    lon : central longitude in degrees
    lat : central latitude in degrees
    sze : size of the edge of the box in degrees
    dateMin : minimum date to use for image search in year-month-day (e.g., 2020-08-01)
    dateMax : maximum date to use for image search in year-month-day (e.g., 2020-08-31)
    vMin : minimum value to select in the Sentinal image pixels (I think this should be close to 0)
    vMax : maximum value to select in the Sentinal image pixels (I think this should be close to 3000)
    filename : output filename for the GeoTIFF image

    Note: it's possible that the vMin and vMax values should be different for each band to make the image look nicer

    https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR
    '''

    print('Downloading Sentinel S2 Surface Reflectance satellite images ... ')

    # define the area of interest, using the Earth Engines geometry object
    coords = [
        [lon - sze / 2., lat - sze / 2.],
        [lon + sze / 2., lat - sze / 2.],
        [lon + sze / 2., lat + sze / 2.],
        [lon - sze / 2., lat + sze / 2.],
        [lon - sze / 2., lat - sze / 2.]
    ]
    aoi = ee.Geometry.Polygon(coords)

    # get the image using Google's Earth Engine
    db = ee.Image(ee.ImageCollection('COPERNICUS/S2_SR') \
                  .filterBounds(aoi) \
                  .filterDate(ee.Date(dateMin), ee.Date(dateMax)) \
                  .sort('CLOUDY_PIXEL_PERCENTAGE') \
                  .first())

    # add the latitude and longitude
    db = db.addBands(ee.Image.pixelLonLat())

    # define the bands that I want to use.  B4 is red, B3 is green, B2 is blue
    # https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR#bands
    bands = ['B4', 'B3', 'B2', 'B1', 'B5', 'B6', 'B7', 'B8A', 'B8', 'B9','B11', 'B12']

    # export geotiff images, these go to Drive and then are downloaded locally
    for selection in bands:
        task = ee.batch.Export.image.toDrive(image=db.select(selection),
                                             description=selection,
                                             scale=30,
                                             region=aoi,
                                             fileNamePrefix=selection,
                                             crs='EPSG:4326',
                                             fileFormat='GeoTIFF')
        task.start()

        url = db.select(selection).getDownloadURL({
            'scale': 30,
            'crs': 'EPSG:4326',
            'fileFormat': 'GeoTIFF',
            'region': aoi})

        r = requests.get(url, stream=True)

        filenameZip = selection + '.zip'
        filenameTif = selection + '.tif'

        # unzip and write the tif file, then remove the original zip file
        with open(filenameZip, "wb") as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

        zipdata = zipfile.ZipFile(filenameZip)
        zipinfos = zipdata.infolist()

        # iterate through each file (there should be only one)
        for zipinfo in zipinfos:
            zipinfo.filename = filenameTif
            zipdata.extract(zipinfo)

        zipdata.close()

    # create a combined RGB geotiff image
    # https://gis.stackexchange.com/questions/341809/merging-sentinel-2-rgb-bands-with-rasterio
    print('Creating 3-band GeoTIFF image ... ')

    # open the image

    B1 = rasterio.open('B1.tif')
    B2 = rasterio.open('B2.tif')
    B3 = rasterio.open('B3.tif')
    B4 = rasterio.open('B4.tif')
    B5 = rasterio.open('B5.tif')
    B6 = rasterio.open('B6.tif')
    B7 = rasterio.open('B7.tif')
    B8 = rasterio.open('B8.tif')
    B8A = rasterio.open('B8A.tif')
    B9 = rasterio.open('B9.tif')
    B11 = rasterio.open('B11.tif')
    B12 = rasterio.open('B12.tif')

    # get the scaling
    image = np.array([B2.read(1), B3.read(1), B4.read(1),
                      B1.read(1), B5.read(1), B6.read(1),
                      B7.read(1), B8.read(1), B8A.read(1),
                      B9.read(1), B11.read(1), B12.read(1)]).transpose(1, 2, 0)
    p2, p98 = np.percentile(image, (2, 98))

    # use the B2 image as a starting point so that I keep the same parameters
    B2_geo = B2.profile
    B2_geo.update({'count': 3})

    with rasterio.open(filename, 'w', **B2_geo) as dest:
        dest.write((np.clip(B12.read(1), p2, p98) - p2) / (p98 - p2) * 255, 1)
        dest.write((np.clip(B11.read(1), p2, p98) - p2) / (p98 - p2) * 255, 2)
        dest.write((np.clip(B9.read(1), p2, p98) - p2) / (p98 - p2) * 255, 3)
        dest.write((np.clip(B8.read(1), p2, p98) - p2) / (p98 - p2) * 255, 1)
        dest.write((np.clip(B8A.read(1), p2, p98) - p2) / (p98 - p2) * 255, 2)
        dest.write((np.clip(B7.read(1), p2, p98) - p2) / (p98 - p2) * 255, 3)
        dest.write((np.clip(B6.read(1), p2, p98) - p2) / (p98 - p2) * 255, 1)
        dest.write((np.clip(B5.read(1), p2, p98) - p2) / (p98 - p2) * 255, 2)
        dest.write((np.clip(B4.read(1), p2, p98) - p2) / (p98 - p2) * 255, 1)
        dest.write((np.clip(B3.read(1), p2, p98) - p2) / (p98 - p2) * 255, 2)
        dest.write((np.clip(B2.read(1), p2, p98) - p2) / (p98 - p2) * 255, 3)
        dest.write((np.clip(B1.read(1), p2, p98) - p2) / (p98 - p2) * 255, 3)

    B1.close()
    B2.close()
    B3.close()
    B4.close()
    B5.close()
    B6.close()
    B7.close()
    B8.close()
    B8A.close()
    B9.close()
    B11.close()
    B12.close()


    # remove the intermediate files
    for selection in bands:
        os.remove(selection + '.tif')
        os.remove(selection + '.zip')


parser = argparse.ArgumentParser(
    prog='satellite_imagery')


parser = argparse.ArgumentParser()
parser.add_argument("--num_images", type=int, help="an integer number")
args = parser.parse_args()

coords = pd.read_csv('station.csv')
coords.drop_duplicates(subset=['LongitudeMeasure', 'LatitudeMeasure'],
                       inplace=True)
coords.sample(frac=1)


size = 0.2
for i in range(args.num_images):
    try:
        if coords.shape[0] <= i:
            print("No more coordinates, downloaded " + str(i))
            break
        loc = coords.iloc[i]
        longitude = loc.LongitudeMeasure
        latitude = loc.LatitudeMeasure
        filename = str(longitude) + '_' + str(latitude)
        getSentinalS2SRImage(longitude, latitude, size, filename + '_1',
                             dateMin='2020-06-01', dateMax='2020-12-31')
        getSentinalS2SRImage(longitude, latitude, size, filename + '_2',
                             dateMin='2020-01-01', dateMax='2020-05-31')
        getSentinalS2SRImage(longitude, latitude, size, filename + '_3',
                             dateMin='2019-06-01', dateMax='2019-12-31')
    except:
        continue
