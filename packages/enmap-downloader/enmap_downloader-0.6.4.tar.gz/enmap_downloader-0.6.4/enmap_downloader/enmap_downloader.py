# SPDX-FileCopyrightText: 2025 GFZ Helmholtz Centre for Geosciences
# SPDX-FileCopyrightText: 2025 Felix Dombrowski
# SPDX-License-Identifier: EUPL-1.2

"""Main module."""

import json
import logging
import re
import tempfile
import time
import itertools
import os
import sys
from pathlib import Path
from typing import List, Tuple

import geopandas
import pandas as pd
import pystac_client
import requests
import tifffile
import numpy as np

from geopandas import GeoDataFrame
from dotenv import load_dotenv
from pystac import ItemCollection
from shapely.geometry import shape

from enmap_downloader.config import Config
from osgeo import gdal
from datetime import datetime
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_transient_http_error(exception):
    if isinstance(exception, requests.exceptions.RequestException):
        if isinstance(exception, requests.exceptions.HTTPError):
            status = exception.response.status_code if exception.response else None
            return status in {
                429,
                500,
                502,
                503,
                504,
                # 403 # CONNECTION FORBIDDEN can be transient due to rate limiting
            }
        return True
    return False

@retry(
    retry=retry_if_exception(is_transient_http_error),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def searchDataAtStac(search_settings: dict, bbox: GeoDataFrame) -> ItemCollection:
    """
    Search data at STAC.

    This function searches for data in a SpatioTemporal Asset Catalog (STAC) using the provided configuration and logs the process.

    Args:
        search_settings (dict): Configuration dictionary containing search parameters.
            - catalog_link (str): URL to the STAC catalog.
            - aoi_settings (dict): Area of interest settings.
                - start_date (str, optional): Start time for the search.
                - end_date (str, optional): End time for the search.
            - collections (list): List of collections to search in.
        bbox (dict): Bounding box coordinates for the area of interest.

    Returns:
        ItemCollection: Collection of items found in the STAC catalog.
    """
    aoi_settings = search_settings.get("aoi_settings", {})
    catalog_link = search_settings.get("catalog_link", "https://geoservice.dlr.de/eoc/ogc/stac/v1/")
    start_date = aoi_settings.get("start_date")
    end_date = aoi_settings.get("end_date")
    time_range = (start_date, end_date) if start_date or end_date else None
    collections = search_settings.get("collections", ["ENMAP_HSI_L2A"])
    logger = logging.getLogger(__name__)

    bbox_clean = bbox.copy()
    bbox_str = bbox_clean.iloc[0].to_dict()

    logger.info("Searching data at STAC for catalog with parameters: \n\tcatalog_link: {}, \n\tcollections: {}, \n\tbbox: {}, \n\ttime_range: {}".format(catalog_link, collections, bbox_str, time_range))

    min_lon, min_lat, max_lon, max_lat = bbox.bounds.iloc[0]
    bbox = [min_lon, min_lat, max_lon, max_lat]

    try:
        catalog = pystac_client.Client.open(catalog_link)
        search = catalog.search(collections= collections, bbox= bbox, datetime= time_range)
        logger.info("{} items found. Cataloguing, this may take a while...".format(search.matched()))
        return search.item_collection()
    except Exception as e:
        raise e

def processItem(
    item,
    result_dir: str,
    download_assets: List[str],
    crop_value: str,
    numpy_flag: bool
):
    """
    Process item.
    This function processes a given item by downloading its metadata and data if specified.
    It creates a directory for the item and logs the process.
    Args:
        item: The item to be processed.
        result_dir: The directory where the results will be saved.
        download_assets: List of assets to be downloaded.
        crop_value: Value how the data should be cropped.
        numpy_flag: Flag to indicate if the data should be saved as numpy array.
    """

    bbox: Tuple[str, geopandas.GeoDataFrame] = item.get("geojson")
    time_range = item.get("time_range")
    item = item.get("item")
    download_assets_copy = download_assets.copy()

    download_path = os.path.join(result_dir, item.collection_id, item.id)
    asset = item.assets.get("image")

    if not os.path.exists(download_path):
        os.makedirs(download_path, exist_ok=True)

    logger = logging.getLogger(__name__)

    file_logger = logging.getLogger(f"item_logger_{item.id}")
    logger_path = os.path.join(download_path, asset.href.rsplit('/', 1)[1])
    fileHandler = logging.FileHandler("{0}/{1}.log".format(os.path.dirname(logger_path), item.id), mode='a')
    logFormatter = logging.Formatter("[%(levelname)-5.5s][%(asctime)s] %(message)s")
    fileHandler.setFormatter(logFormatter)
    file_logger.addHandler(fileHandler)
    file_logger.setLevel(logging.INFO)
    metadata = None

    if "properties" in download_assets_copy:
        file_path = os.path.join(download_path, item.id + ".json")
        if os.path.exists(file_path):
            logger.info("Asset [properties] already exists for item: {}".format(item.id))
            try:
                with open(file_path, "r") as f:
                    metadata = json.load(f)
            except Exception as e:
                logger.error("Error reading asset [properties] for item {}: {}".format(item.id, e))
        else:
            try:
                asset_link = f"https://geoservice.dlr.de/eoc/ogc/stac/v1/collections/{item.collection_id}/items/{item.id}?f=application/geo%2Bjson"
                logger.info("Asset [properties] started for item: {}".format(item.id))
                metadata = downloadItemProperties(asset_link, file_path, file_logger)
                logger.info("Asset [properties] download completed for item: {}".format(item.id))
            except Exception as e:
                logger.error("Error downloading asset [properties] for item {}: {}".format(item.id, e))
        download_assets_copy.remove("properties")

    if "metadata" in download_assets_copy:
        asset_link = item.assets.get("metadata")

        file_path = os.path.join(download_path, asset_link.href.rsplit('/', 1)[1])
        if os.path.exists(file_path):
            logger.info("Asset [metadata] already exists for item: {}".format(item.id))
        else:
            try:
                logger.info("Asset [metadata] download started for item: {}".format(item.id))
                downloadItemMetadata(asset_link.href, file_path, file_logger)
                logger.info("Asset [metadata] download completed for item: {}".format(item.id))
            except Exception as e:
                logger.error("Error downloading asset [metadata] for item {}: {}".format(item.id, e))
        download_assets_copy.remove("metadata")

    for asset in download_assets_copy:
        asset_link = item.assets.get(asset)

        file_path = os.path.join(download_path, asset_link.href.rsplit('/', 1)[1])
        if os.path.exists(file_path):
            logger.info("Asset [{}] already exists for item: {}".format(asset, item.id))
        else:
            try:
                logger.info("Asset [{}] download started for item: {}".format(asset, item.id))
                downloadItemData(bbox, item, crop_value, time_range, asset_link, file_path, numpy_flag, file_logger)
                logger.info("Asset [{}] download download completed for item: {}".format(asset, item.id))
            except Exception as e:
                logger.error("Error downloading asset [{}] for item {}: {}".format(asset, item.id, e))

    # if metadata_flag and metadata:
    #     flat = json_normalize(metadata)
    #     row = flat.iloc[0].to_dict()
    #     row["asset_id"] = asset.href
    #     row["download_path"] = download_path
    #     return row
    return

def init_gdal():
    gdal.SetConfigOption("GDAL_HTTP_MAX_RETRY", "3")
    gdal.SetConfigOption("GDAL_HTTP_RETRY_DELAY", "1")
    gdal.SetConfigOption("GDAL_HTTP_RETRY_DELAY_BACKOFF", "2")  # exponential
    gdal.SetConfigOption("GDAL_HTTP_USERAGENT", "Mozilla/5.0")  # some servers choke on GDAL UA
    gdal.SetConfigOption("CPL_VSIL_CURL_USE_HEAD", "NO")
    gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "YES")

@retry(
    retry=retry_if_exception(is_transient_http_error),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def downloadItemData(
    bbox : Tuple[str, geopandas.GeoDataFrame],
    item,
    crop_value,
    time_range,
    asset,
    file_path,
    is_numpy,
    logger):

    try:
        start = time.time()
        gdal.UseExceptions()
        gdal.AllRegister()
        # init_gdal()
        # gdal.SetConfigOption("GDAL_HTTP_MAX_RETRY", "3")
        # gdal.SetConfigOption("GDAL_HTTP_RETRY_DELAY", "2")
        geojson_path, geojson = bbox

        if geojson is not None:
            if crop_value == "precise":
                logger.info(f"Cropping data to precise area: {geojson.geometry}, using {geojson.to_string()}, time_frame: {time_range}")
            if crop_value == "bbox":
                logger.info(f"Cropping data to bounding box: {geojson.total_bounds}, using {geojson.to_string()}, time_frame: {time_range}")
            if crop_value == "default":
                logger.info(f"Downloading data without cropping, using {geojson.to_string()}, time_frame: {time_range}")

        data = gdal.Open("/vsicurl/" + asset.href)
        if data is None:
            raise RuntimeError(f"Failed to open asset: {asset.href}")

        if crop_value in ["precise", "bbox"]:
            transform = data.GetGeoTransform()
            warp_options = {}

            if crop_value == "precise":


                poly1 = geojson.geometry.iloc[0]
                poly2 = shape(item.geometry)

                intersection = poly1.intersection(poly2)

                geojson_obj = intersection.__geo_interface__
                with tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".geojson") as tmp:
                    json.dump(geojson_obj, tmp)
                    tmp.flush()
                    tmp_path = tmp.name

                    # print("Saved to:", tmp_path)

                    warp_options = {
                        'cutlineDSName': tmp_path,
                        'cropToCutline': True,
                        'dstNodata': -32768,
                    }

                    gdal.Warp(
                        file_path,
                        data,
                        xRes=transform[1],
                        yRes=transform[5],
                        format="GTiff",
                        **warp_options,
                    )

            elif crop_value == "bbox":
                gdal.Warp(
                    file_path,
                    data,
                    outputBounds=geojson.total_bounds,
                    xRes=transform[1],
                    yRes=transform[5],
                    format="GTiff",
                    **warp_options,
                )


        elif crop_value == "default":
            gdal.Warp(
                file_path,
                data,
                format="GTiff"
            )

        del data

        if is_numpy:
            logger.info(f"Converting {file_path} to numpy array")
            array = tifffile.imread(file_path)
            npy_path = file_path.replace('.tif', '.npy')
            np.save(npy_path, array)
            os.remove(file_path)
            logger.info(f"Saved numpy array to {npy_path}")

        logger.info(f"Downloaded item in {(time.time() - start):.2f} seconds")
    except Exception as e:
        logger.error(e)
        logger.error(e.args)
        raise e

@retry(
    retry=retry_if_exception(is_transient_http_error),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def downloadItemProperties(asset, file_path, logger):
    try:
        with requests.get(asset) as response:
            response.raise_for_status()
            data = response.json()
            with open(file_path, "w") as out_file:
                json.dump(data["properties"], out_file, indent=4)
            return data["properties"]
    except Exception as e:
        logger.error(e)

@retry(
    retry=retry_if_exception(is_transient_http_error),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def downloadItemMetadata(asset, file_path, logger):
    """

    Download item metadata in form of xml file
    Args:
        asset:
        file_path:
        logger:

    Returns:
        bool:


    """
    try:
        with requests.get(asset) as response:
            response.raise_for_status()
            with open(file_path, "wb") as out_file:
                out_file.write(response.content)
            return True
    except Exception as e:
        logger.error(e)

def importGeoJson(path) -> List[Tuple[str, geopandas.GeoDataFrame]]:
    """
    Import GeoJSON files.

    This function imports GeoJSON files from a given path and returns a list of GeoJSON objects.

    Args:
        path (str): The path to the GeoJSON file or directory containing GeoJSON files.

    Returns:
        list: A list of imported GeoJSON objects.

    Raises:
        Exception: If the path is invalid or does not contain GeoJSON files, it logs the error.
    """
    logger = logging.getLogger(__name__)
    geojson_list = []

    if os.path.isdir(path):
        files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".geojson")]
    elif os.path.isfile(path) and path.endswith(".geojson"):
        files = [path]
    else:
        raise logger.error(f"Invalid path {path}: Must be a GeoJSON file or a directory containing GeoJSON files.")

    for file in files:
        try:
            geojson_list.append((file, geopandas.read_file(file)))
        except Exception as e:
            logger.error(e)
    return geojson_list

def downloadEnmapData(config: dict, in_parallel : bool = False, limit: int = None, num_workers = None):
    """
    Download Enmap data worker.

    This function downloads data from a given asset URL and saves it to the specified download path.
    It supports saving the data in different formats such as JSON and NPY.

    Args:
        config: Configuration dictionary containing search parameters.
        in_parallel: Flag to indicate if the download should be done in parallel.
        limit: The maximum number of items to download.
        num_workers: The number of workers to use for parallel processing.

    Raises:
        Exception: If there is an error during the download or saving process, it logs the error.
    """

    result_settings = config.get("result_settings", {})
    search_settings = config.get("search_settings", {})
    aoi_settings = search_settings.get("aoi_settings", {})
    download_assets = result_settings.get("download_assets", [])
    crop_value = result_settings.get("crop_value", "default")
    result_dir = result_settings.get("results_dir", "/data")
    bbox_list = aoi_settings.get("geojson", "")
    numpy_flag = result_settings.get("result_format", "tif") == "npy"

    logger = logging.getLogger(__name__)

    logger.info("Enmap downloader started.")

    geojsons = importGeoJson(bbox_list)

    if len(geojsons) == 0:
        logger.error("No geojsons found in the given path")

    linked_catalog = []

    start_date = aoi_settings.get("start_date")
    end_date = aoi_settings.get("end_date")
    time_range = (start_date, end_date) if start_date or end_date else None

    try:
        for geojson in geojsons:
            search = searchDataAtStac(search_settings, geojson[1])

            if search is None:
                continue

            for item in search:
                linked_catalog.append({
                    "geojson": geojson,
                    "time_range": time_range,
                    "item": item
                })
    except Exception as e:
        logger.error("Error retrieving data from STAC catalogue: {}".format(e))


    if len(linked_catalog) == 0:
        logger.info("No items found for given parameters.")
        return

    if not download_assets:
        logger.info("Parameter download_assets is empty. No data will be downloaded.")
        return

    items_to_process = list(itertools.islice(linked_catalog, limit))

    results = []

    # if in_parallel:
    #
    #     with ThreadPoolExecutor(max_workers=num_workers) as executor:
    #         futures = [
    #             executor.submit(
    #                 processItem,
    #                 item,
    #                 result_dir,
    #                 crop_value,
    #                 numpy_flag
    #             )
    #             for item in items_to_process
    #         ]
    #
    #     for future in tqdm(futures, total=len(futures), desc="Processing items"):
    #         try:
    #             result = future.result()
    #             if result is not None:
    #                 results.append(result)
    #         except Exception as e:
    #             logger.error(f"Error processing item: {e}")

    for item in tqdm(items_to_process, desc="Processing items"):

        try:
            result = processItem(
                item,
                result_dir,
                download_assets,
                crop_value,
                numpy_flag
            )
            if result is not None:
                results.append(result)
        except Exception as e:
            logger.error(f"Error processing item: {e}")

    logger.info("Enmap downloader finished.")
    metadata_df = pd.DataFrame(results)
    return metadata_df

def credential_parser(username, password, machine="download.geoservice.dlr.de", netrc_path=None):
    logger = logging.getLogger(__name__)

    if netrc_path is None:
        netrc_path = Path.home() / ".netrc"
    else:
        netrc_path = Path(netrc_path)

    # Build new entry
    new_entry = f"machine {machine} login {username} password {password}\n"

    # If file exists, read and potentially update
    if netrc_path.exists():
        with netrc_path.open("r") as f:
            content = f.read()

        pattern = re.compile(rf"machine {re.escape(machine)} login (\S+) password (\S+)")
        match = pattern.search(content)

        if match:
            old_username, old_password = match.groups()
            if old_username == username and old_password == password:
                logger.info(f"Credentials for '{machine}' already exist and are up to date.")
                return
            else:
                logger.info(f"Updating credentials for '{machine}'.")
                content = pattern.sub(new_entry, content)
        else:
            logger.info(f"Adding new entry for '{machine}'.")
            if content and not content.endswith("\n"):
                content += "\n"
            content += new_entry + "\n"
    else:
        logger.info(f"Creating .netrc and adding entry for '{machine}'.")
        content = new_entry + "\n"

    with netrc_path.open("w") as f:
        f.write(content)

    # Secure the file (Unix-only)
    try:
        os.chmod(netrc_path, 0o600)
    except Exception as e:
        logger.error(f"Warning: Could not set permissions on {netrc_path}: {e}")
    logger.info(f"Credentials saved for machine '{machine}' in {netrc_path}")

def init_logger(config):
    result_settings = config.get("result_settings", {})
    logging_dir = result_settings.get("logging_dir", "../logs")
    logging_level = result_settings.get("logging_level", logging.INFO)
    logFormatter = logging.Formatter("[%(levelname)-5.5s][%(asctime)s][%(lineno)d] %(message)s")
    os.makedirs(logging_dir, exist_ok=True)
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fileHandler = logging.FileHandler("{0}/{1}.log".format(logging_dir, f"enMapDownloader_{current_datetime}"),mode='w')
    fileHandler.setFormatter(logFormatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(fileHandler)
    logger.setLevel(logging_level)
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

def enmapDownloader(
    config_dict: dict,
    # in_parallel : bool = False,
    limit: int = None,
    # num_workers: int = None,
    username : str = None,
    password: str = None):
    """
    This function initializes the logger, loads the configuration, checks for credentials in the .env file,
    and starts the download process for Enmap data.
    Args:
        config_dict (dict): Configuration dictionary containing search parameters.
        in_parallel (bool): Flag to indicate if the download should be done in parallel.
        limit (int, optional): The maximum number of items to download.
        num_workers (int, optional): The number of workers to use for parallel processing.
        username (str, optional): Username for authentication.
        password (str, optional): Password for authentication.
    """

    config_dict = Config(**config_dict).model_dump(by_alias=True)
    init_logger(config_dict)
    logger = logging.getLogger(__name__)

    if username is not None and password is not None:
        logger.info("Using provided username and password for authentication.")
        credential_parser(username, password)

    else:
        if not os.path.exists(".env"):
            with open(".env", "w") as env_file:
                env_file.write("ENMAP_USERNAME=myusername\nENMAP_PASSWORD=mypassword")
                print(".env file created, please fill in username and password")
                return
        load_dotenv()
        username = os.getenv('ENMAP_USERNAME')
        password = os.getenv('ENMAP_PASSWORD')
        logger.info("Using credentials from .env file for authentication.")
        credential_parser(username, password)

    # TODO: do we just remove this?
    in_parallel = False
    num_workers = None

    return downloadEnmapData(config_dict, in_parallel, limit=limit, num_workers=num_workers)
