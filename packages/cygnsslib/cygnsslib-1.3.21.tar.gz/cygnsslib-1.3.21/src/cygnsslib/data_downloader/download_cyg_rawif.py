import datetime as dt
import fnmatch
from typing import Optional, Union
import numpy as np
import os
import warnings
from cygnsslib.data_downloader.download_cygnss import download_cyg_files, download_cyg_files_between_date


def download_rawif_cyg_files_between_date(st_date: dt.date, end_date: dt.date, list_sc_num: Optional[Union[list[int], int]] = None,
                                          cyg_data_ver: Optional[str] = None, cygnss_l1_path: Optional[str] = None,
                                          checksum_exist_file: bool = False, force_download: bool = False, download_l1_data: bool = False):
    """
    download RAWIF CYGNSS data between two dates (including start and end date)

    :param st_date: start date
    :param end_date: end date
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH')), see description for more details
    :param force_download: re-download the file if it exist?
    :param download_l1_data: when there is a Rawif data, download its L1 data with it, env $CYGNSS_L1_PATH var should point to the folder of L1 data.
    :param cyg_data_ver: CYGNSS data L1 data version
    :param checksum_exist_file: apply check sum to existing files
    :return:
    """
    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get('CYGNSS_L1_PATH')

    # check if the folder name is not raw_if, if not, change the folder name
    folder_list = cygnss_l1_path.split(os.path.sep)
    if not folder_list[-1]:
        folder_list.pop(-1)
    if 'raw_if' not in folder_list[-1]:
        folder_list[-1] = 'raw_if'
    cyg_rawif_path = os.sep.join(folder_list)

    cyg_data_lvl = 'RAW'
    download_cyg_files_between_date(st_date, end_date, list_sc_num, cyg_data_ver, cyg_data_lvl, cyg_rawif_path, checksum_exist_file, force_download)
    if download_l1_data:
        cyg_data_lvl = 'L1'
        download_cyg_files_between_date(st_date, end_date, list_sc_num, cyg_data_ver, cyg_data_lvl, cygnss_l1_path, checksum_exist_file, force_download)


def download_cyg_rawif_files(data_year: int, list_data_day: Union[list[int], int], list_sc_num: Optional[Union[list[int], int]] = None,
                             cyg_data_ver: Optional[str] = None, cygnss_l1_path: Optional[str] = None, checksum_exist_file: bool = False,
                             force_download: bool = False, download_l1_data: bool = False):
    """

    download the raw_if cygnss data,
    if cygnss_l1_path or os.environ.get('CYGNSS_L1_PATH') point to a folder with name not "raw_if", it will save the data in a raw_if folder in the
    parent dir.

    :param data_year: list of data years
    :param list_data_day: list of data days
    :param list_sc_num: list of cygnss spacecraft numbers (1-8), if None will download all SCs
    :param cygnss_l1_path: path of the cygnss L1 data (default: os.environ.get('CYGNSS_L1_PATH')), see description for more details
    :param force_download: re-download the file if it exist?
    :param download_l1_data: when there is a Rawif data, download its L1 data with it, env $CYGNSS_L1_PATH var should point to the folder of L1 data.
    :param cyg_data_ver: CYGNSS data L1 data version
    :param checksum_exist_file: apply check sum to existing files
    :return:
    """
    if cygnss_l1_path is None:
        cygnss_l1_path = os.environ.get('CYGNSS_L1_PATH')

    # check if the folder name is not raw_if, if not, change the folder name
    folder_list = cygnss_l1_path.split(os.path.sep)
    if not folder_list[-1]:
        folder_list.pop(-1)
    if 'raw_if' not in folder_list[-1]:
        folder_list[-1] = 'raw_if'
    cyg_rawif_path = os.sep.join(folder_list)

    cyg_data_lvl = 'raw'
    download_cyg_files(data_year, list_data_day, list_sc_num, cyg_data_ver, cyg_data_lvl, cyg_rawif_path, checksum_exist_file, force_download)

    if download_l1_data:
        cyg_data_lvl = 'L1'
        download_cyg_files(data_year, list_data_day, list_sc_num, cyg_data_ver, cyg_data_lvl, cygnss_l1_path, checksum_exist_file, force_download)


def get_cyg_rawif_files(cyg_day_folder, sc_num):
    """
    check if the file exist and return the file name, if not exist return None.
    if exist it will return list of the files

    :param cyg_day_folder: cygnss day folder
    :type cyg_day_folder: str
    :param sc_num: spacecraft number
    :type sc_num: int
    :return: file name
    :rtype: str
    """
    _files_flag = np.zeros(2).astype(bool)
    result = []
    pattern = "cyg{:02d}*.bin".format(sc_num)
    for root, dirs, files in os.walk(cyg_day_folder):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)

    if len(result) == 0:
        return None
    else:
        files_name_list = list()
        for file_name in result:
            if 'data' in file_name:
                _files_flag[0] = True
                files_name_list.append(file_name)
            elif 'meta' in file_name:
                _files_flag[1] = True
                files_name_list.append(file_name)

    if not _files_flag.all():
        warnings.warn(f"couldn't find both data and the metadata files in {cyg_day_folder:s}, sc: {sc_num:d}, try to download both",
                      RuntimeWarning)
        return None

    return files_name_list


if __name__ == '__main__':
    down_start_date = dt.date(year=2020, month=8, day=4)
    down_end_date = dt.date(year=2020, month=8, day=4)
    download_rawif_cyg_files_between_date(down_start_date, down_end_date)
    download_cyg_rawif_files(data_year=2020, list_data_day=227)
