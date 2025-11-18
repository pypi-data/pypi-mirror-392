#!/usr/bin/env python3
"""
 DESCRIPTION
          This tool is part of cygnsslib python package. The package is created by Mixil lab at USC
          See <https://bitbucket.org/usc_mixil/cygnss-library>

          This Tool download CYGNSS data

 AUTHOR   Amer Melebari
          Microwave Systems, Sensors and Imaging Lab (MiXiL)
          University of Southern California
 EMAIL    amelebar@usc.edu
 CREATED  2020‑07‑19
 Updated  2023-05-02

  Copyright 2023 University of Southern California
"""
import logging
from inspect import signature
from typing import Optional, Union
from cygnsslib.data_downloader.download_srtm import EarthdataSession
import subscriber.podaac_access as pa
from time import sleep
from tqdm.auto import tqdm
import datetime as dt
import fnmatch
import hashlib
import numpy as np
import os
import requests
import shutil
import warnings
from urllib.error import HTTPError


CYG_MIN_FILE_SIZE = 50e6  # in bytes
PODAAC_CYG_URL = 'https://podaac-tools.jpl.nasa.gov/drive/files/allData/cygnss'
OPEN_DAP_URL = 'https://opendap.jpl.nasa.gov/opendap/allData/cygnss'
L1_VER = 'v3.2'
CHUNK_SIZE = 1024 * 1024  # 1 MB
MAX_CONNECTIONS_TRIES = 10
page_size = 2000


def cyg_ver2shortname(cyg_ver: str, cyg_data_level: str):
    if 'raw' in cyg_data_level.lower():
        return 'CYGNSS_L1_RAW_IF'
    else:
        return f'CYGNSS_{cyg_data_level.upper():s}_{cyg_ver.upper():s}'


def checksum(file_path, chunk_num_blocks=4096):
    """
    do md5 checksum for large files

    :param file_path: file path
    :type file_path: str
    :param chunk_num_blocks: number of blocks in a chunk
    :type chunk_num_blocks: int
    :return:
    """

    h = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_num_blocks * h.block_size):
            h.update(chunk)
    return h.hexdigest()


def download_file(file_url: str, output_folder: str, auth: Optional[tuple[str, str]] = None, url_md5_checksum: Optional[str] = None) -> Optional[str]:
    """
    download the file with url into folder output_folder

    :param file_url: url of the file
    :type file_url: str
    :param output_folder: saving folder
    :type output_folder: str
    :param auth: username or pass
    :type auth: tuple of str or None
    :param url_md5_checksum: md5 checksum of the downloaded file, if None, the code will find it
    :type url_md5_checksum: str
    :return: downloaded file path
    :rtype: str
    """
    num_redownload = 0
    file_name = file_url.split('/')[-1]
    out_file = os.path.join(output_folder, file_name)
    out_file_temp = f'{out_file:s}.incomplete'
    for i_try in range(MAX_CONNECTIONS_TRIES):
        try:
            with EarthdataSession(username=auth[0], password=auth[1]) as session:
                with session.get(file_url, stream=True) as response:
                    if response.status_code == 404:
                        return None
                    elif response.status_code == 401:  # Auth Error
                        raise requests.exceptions.RequestException
                    response.raise_for_status()
                    response.raw.decode_content = True
                    file_size = int(response.headers.get('content-length', 0))
                    free_disk_space = shutil.disk_usage(output_folder).free
                    if file_size > free_disk_space:
                        def bytes2mb(x: float) -> int: return int(x / 1024 / 1024)
                        raise IOError(f'No enough space in the disk. file size: {bytes2mb(file_size):d} MB, free space {bytes2mb(free_disk_space):d}')
                    file_screen_name = f'...{os.sep.join(out_file_temp.split(os.sep)[-4:])[:-11]}' if (len(out_file_temp) > 80) else out_file_temp
                    with tqdm.wrapattr(open(out_file_temp, "wb"), "write", miniters=1, total=file_size, desc=file_screen_name) as target_file:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            target_file.write(chunk)
                if url_md5_checksum is None:  # get md5 checksum
                    url_md5_checksum = session.get(f'{file_url:s}.md5').content.strip().decode('utf').split()[0]
                if url_md5_checksum:  # if the md5 file available
                    file_checksum = checksum(out_file_temp)
                    if url_md5_checksum != file_checksum:
                        raise RuntimeError
                else:
                    print(f'MD5 checksum is not available for this file; {file_name:s}')
        except RuntimeError:  # MD5 verification failed
            if i_try < MAX_CONNECTIONS_TRIES and num_redownload < 2:
                print("MD5 checksum failed! Trying to re-download it again")
                os.remove(out_file_temp)
                num_redownload += 1
            else:
                print("MD5 checksum failed!")
                shutil.move(out_file_temp, out_file)
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            if i_try < MAX_CONNECTIONS_TRIES:
                print('Connection Error sleep for 5 sec')
                sleep(5)
            else:
                raise RuntimeError(f'a connection error was raised when trying to access {file_url:s}')
        else:  # if it was successful
            shutil.move(out_file_temp, out_file)
            break
    return out_file


def download_cyg_files(data_year: int, list_data_day: Union[list[int], int], list_sc_num: Optional[Union[list[int], int]] = None,
                       cyg_data_ver: Optional[str] = None, cyg_data_lvl: str = 'L1', cygnss_l1_path: Optional[str] = None,
                       checksum_exist_file: bool = False, force_download: bool = False):
    """
    
    download multiple CYGNSS files
    
    :param data_year: data year
    :type data_year: int
    :param list_data_day: list of data days
    :type list_data_day: list or int or np.array
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or int or np.array or None
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :param cyg_data_lvl: cygnss data level (ex: 'L1')
    :type cyg_data_lvl: str
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH'))
    :type cygnss_l1_path: str or None
    :param checksum_exist_file: check md5 checksum for existing files? this will make it very slow
    :type checksum_exist_file: bool
    :param force_download: re-download the file even if the version is not included in the path (not recommended)
    :type force_download: bool
    :return:
    """
    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get('CYGNSS_L1_PATH')
    if np.size(list_data_day) == 1:
        list_data_day = [int(list_data_day)]
    if list_sc_num is None:
        list_sc_num = np.arange(1, 9)
    elif np.size(list_sc_num) == 1:
        list_sc_num = [int(list_sc_num)]
    search_keywords = [f'cyg{sc_num:02d}' for sc_num in list_sc_num]
    if cygnss_l1_path is None:
        raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    if cyg_data_ver is None:
        folder_list = cygnss_l1_path.split(os.path.sep)
        if not folder_list[-1]:
            folder_list.pop(-1)
        cyg_data_ver = folder_list[-1]
    cyg_data_lvl = cyg_data_lvl.upper()

    # get temporal limit for the search
    start_date_time = dt.datetime(data_year, 1, 1) + dt.timedelta(days=min(list_data_day) - 1)
    end_date_time = dt.datetime(data_year, 1, 1, 23, 59, 59) + dt.timedelta(days=max(list_data_day) - 1)
    temporal_range = pa.get_temporal_range(start_date_time.isoformat() + 'Z', end_date_time.isoformat() + 'Z',
                                           dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))

    # Get CYGNSS Shortname
    cyg_data_shortname = cyg_ver2shortname(cyg_data_ver, cyg_data_lvl)

    pa.setup_earthdata_login_auth(pa.edl)
    token = pa.get_token(pa.token_url)

    params = [
        ('page_size', page_size),
        ('sort_key', "start_date"),
        ('provider', 'POCLOUD'),
        ('ShortName', cyg_data_shortname),
        ('temporal', temporal_range),
        ('token', token),
    ]

    # If 401 is raised, refresh token and try one more time
    try:
        results = pa.get_search_results(params)
    except HTTPError as e:
        if e.code == 401:
            token = pa.refresh_token(token)
            # Updated: This is not always a dictionary...
            # in fact, here it's always a list of tuples
            for i, p in enumerate(params):
                if p[0] == "token":
                    params[i] = ("token", token)
            results = pa.get_search_results(params)
        else:
            raise e

    checksums = pa.extract_checksums(results)
    file_start_times = pa.parse_start_times(results)

    downloads = []
    for r in results['items']:
        for u in r['umm']['RelatedUrls']:
            if u['Type'] == "GET DATA" and ('Subtype' not in u or u['Subtype'] != "OPENDAP DATA"):
                f = u['URL']
                data_date_str = r['umm']['TemporalExtent']['RangeDateTime']['BeginningDateTime']
                data_date = dt.datetime.fromisoformat(data_date_str[:-1]).date()
                doy = data_date.timetuple().tm_yday
                if doy not in list_data_day:
                    continue
                for extension in ["\\.nc"]:
                    if pa.search_extension(extension, f):
                        for keyword in search_keywords:
                            if keyword in f.lower():
                                downloads.append(f)
                                break
    ver_folder_exist = check_ver_folder(cygnss_l1_path, cyg_data_ver)
    if not force_download and not ver_folder_exist:
        error_str = f"You are trying to download version {cyg_data_ver:s}, but the path doesn't contain the version name"
        raise ValueError(f'{error_str:s}\nuse force_download=True to remove this error')

    success_cnt = failure_cnt = skip_cnt = 0
    downloaded_files_list = []
    for f in downloads:
        try:
            output_path = prepare_time_output(file_start_times, cygnss_l1_path, f)

            # decide if we should actually download this file (e.g. we may already have the latest version)
            if os.path.exists(output_path) and not force_download and (not checksum_exist_file or pa.checksum_does_match(output_path, checksums)):
                logging.info(str(dt.datetime.now()) + " SKIPPED: " + f)
                skip_cnt += 1
                continue
            if len(list(signature(pa.download_file).parameters)) > 3:  # allow for the use of non MiXIL version
                checksum_val = checksums.get(os.path.basename(output_path))
                pa.download_file(f, output_path, checksum_val)
            else:
                pa.download_file(f, output_path)
            logging.info(str(dt.datetime.now()) + " SUCCESS: " + f)
            success_cnt += 1

        except Exception:
            logging.warning(str(dt.datetime.now()) + " FAILURE: " + f, exc_info=True)
            failure_cnt += 1
        else:
            downloaded_files_list.append(output_path)
    return downloaded_files_list


def prepare_time_output(times: list[tuple], prefix: str, file: str) -> str:
    """
    Create output directory using:
        OUTPUT_DIR/YEAR/DAY_OF_YEAR/

    Parameters
    ----------
    times : list
        list of tuples consisting of granule names and start times
    prefix : string
        prefix for output path, either custom output -d or short name
    file : string
        granule file name

    Returns
    -------
    write_path
        string path to where granules will be written
    """

    time_match = [_dt for _dt in times if _dt[0] == os.path.splitext(os.path.basename(file))[0]]

    # Found on 11/11/21
    # https://github.com/podaac/data-subscriber/issues/28
    # if we don't find the time match array, try again using the
    # filename AND its suffix (above removes it...)
    if len(time_match) == 0:
        time_match = [_dt for _dt in times if _dt[0] == os.path.basename(file)]
    time_match = time_match[0][1]

    year = time_match.strftime('%Y')
    month = time_match.strftime('%m')
    day = time_match.strftime('%d')
    day_of_year = time_match.strftime('%j')

    time_dir = os.path.join(year, day_of_year)
    pa.check_dir(os.path.join(prefix, time_dir))
    write_path = os.path.join(prefix, time_dir, os.path.basename(file))
    return write_path


def download_cyg_files_between_date(st_date: dt.date, end_date: dt.date, list_sc_num: Optional[Union[list[int], int]] = None,
                                    cyg_data_ver: Optional[str] = None, cyg_data_lvl: str = 'L1', cygnss_l1_path: Optional[str] = None,
                                    checksum_exist_file: bool = False, force_download: bool = False):
    """
    download CYGNSS data between two dates (including start and end date)

    :param st_date: start date
    :type st_date: date
    :param end_date: end date
    :type end_date: date
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :type list_sc_num: list or np.array or int
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :param cyg_data_lvl: cygnss data level (ex: 'L1')
    :type cyg_data_lvl: str
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH'))
    :type cygnss_l1_path: str or None
    :param checksum_exist_file: check md5 checksum for existing files? this will make it very slow
    :type checksum_exist_file: bool
    :param force_download: download the file even if the version is not included in the path (not recommended)
    :return:
    """

    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get('CYGNSS_L1_PATH')
    if list_sc_num is None:
        list_sc_num = np.arange(1, 9)
    elif np.size(list_sc_num) == 1:
        list_sc_num = [int(list_sc_num)]
    search_keywords = [f'cyg{sc_num:02d}' for sc_num in list_sc_num]
    if cygnss_l1_path is None:
        raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    if cyg_data_ver is None:
        folder_list = cygnss_l1_path.split(os.path.sep)
        if not folder_list[-1]:
            folder_list.pop(-1)
        cyg_data_ver = folder_list[-1]
    cyg_data_lvl = cyg_data_lvl.upper()

    # get temporal limit for the search
    start_date_time = st_date.isoformat() + 'T00:00:00Z'
    end_date_time = end_date.isoformat() + 'T23:59:59Z'
    temporal_range = pa.get_temporal_range(start_date_time, end_date_time, dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))

    # Get CYGNSS Shortname
    cyg_data_shortname = cyg_ver2shortname(cyg_data_ver, cyg_data_lvl)

    pa.setup_earthdata_login_auth(pa.edl)
    token = pa.get_token(pa.token_url)

    params = [
        ('page_size', page_size),
        ('sort_key', "start_date"),
        ('provider', 'POCLOUD'),
        ('ShortName', cyg_data_shortname),
        ('temporal', temporal_range),
        ('token', token),
    ]

    # If 401 is raised, refresh token and try one more time
    try:
        results = pa.get_search_results(params)
    except HTTPError as e:
        if e.code == 401:
            token = pa.refresh_token(token)
            # Updated: This is not always a dictionary...
            # in fact, here it's always a list of tuples
            for i, p in enumerate(params):
                if p[0] == "token":
                    params[i] = ("token", token)
            results = pa.get_search_results(params)
        else:
            raise e

    checksums = pa.extract_checksums(results)
    file_start_times = pa.parse_start_times(results)

    downloads = []
    for r in results['items']:
        for u in r['umm']['RelatedUrls']:
            if u['Type'] == "GET DATA" and ('Subtype' not in u or u['Subtype'] != "OPENDAP DATA"):
                f = u['URL']
                for extension in ["\\.nc"]:
                    if pa.search_extension(extension, f):
                        for keyword in search_keywords:
                            if keyword in f.lower():
                                downloads.append(f)
                                break
    ver_folder_exist = check_ver_folder(cygnss_l1_path, cyg_data_ver)
    if not force_download and not ver_folder_exist:
        error_str = f"You are trying to download version {cyg_data_ver:s}, but the path doesn't contain the version name"
        raise ValueError(f'{error_str:s}\nuse force_download=True to remove this error')

    success_cnt = failure_cnt = skip_cnt = 0
    downloaded_files_list = []

    for f in downloads:
        try:
            output_path = prepare_time_output(file_start_times, cygnss_l1_path, f)

            # decide if we should actually download this file (e.g. we may already have the latest version)
            if os.path.exists(output_path) and not force_download and (not checksum_exist_file or pa.checksum_does_match(output_path, checksums)):
                logging.info(str(dt.datetime.now()) + " SKIPPED: " + f)
                skip_cnt += 1
                continue

            if len(list(signature(pa.download_file).parameters)) > 3:  # allow for the use of non MiXIL version
                checksum_val = checksums.get(os.path.basename(output_path))
                pa.download_file(f, output_path, checksum_val)
            else:
                pa.download_file(f, output_path)

            logging.info(str(dt.datetime.now()) + " SUCCESS: " + f)
            success_cnt += 1

        except Exception:
            logging.warning(str(dt.datetime.now()) + " FAILURE: " + f, exc_info=True)
            failure_cnt += 1
        else:
            downloaded_files_list.append(output_path)
    return downloaded_files_list


def get_cyg_calibrated_rawif_file(cyg_day_folder: str, sc_num, sampling_rate: float) -> Optional[str]:
    """ Get file name if exist from rawif with specific sampling rate"""
    result = []
    pattern = f"cyg{sc_num:02d}*_rate_{sampling_rate:.3f}*.nc"
    for root, dirs, files in os.walk(cyg_day_folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
                break  # finding the first file

    if len(result) == 0:
        cyg_file_name = None
    else:
        cyg_file_name = result[0]
    return cyg_file_name


def get_cyg_file(cyg_day_folder: str, sc_num: int) -> Optional[str]:
    """
    check if the file exist and return the file name, if not exist return None

    :param cyg_day_folder: cygnss day folder
    :type cyg_day_folder: str
    :param sc_num: spacecraft number
    :type sc_num: int
    :return: file name
    :rtype: str
    """
    result = []
    pattern = f"cyg{sc_num:02d}*.nc"
    for root, dirs, files in os.walk(cyg_day_folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
                break  # finding the first file

    if len(result) == 0:
        cyg_file_name = None
    else:
        cyg_file_name = result[0]

    return cyg_file_name


def check_ver_folder(cygnss_l1_path: str, cyg_data_ver: str) -> bool:
    """
    check if the version name in the path

    :param cygnss_l1_path: path of the cygnss L1 data
    :type cygnss_l1_path: str
    :param cyg_data_ver: cygnss data version (ex: 'v2.1')
    :type cyg_data_ver: str
    :return:
    """
    path_split = cygnss_l1_path.split(os.sep)
    if cyg_data_ver in path_split:
        out = True
    else:
        warnings.warn(f"You are trying to download version {cyg_data_ver:s}, but the path doesn't contain the version name", RuntimeWarning)
        out = False
    return out


if __name__ == "__main__":

    st_date = dt.date(year=2020, month=7, day=1)
    end_date = dt.date(year=2020, month=12, day=31)
    cyg_data_ver = 'v3.1'
    download_cyg_files(2019, [5, 30, 31, 40])
    download_cyg_files_between_date(st_date, end_date, cyg_data_ver=cyg_data_ver, checksum_exist_file=False)
