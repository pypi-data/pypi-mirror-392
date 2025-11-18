from time import sleep
from typing import Optional
import os
import requests
import shutil
import zipfile


ANT_PTRN_URL = 'https://bitbucket.org/usc_mixil/cygnss_antenna_patterns/get/master.zip'
MAX_CONNECTIONS_TRIES = 5
CHUNK_SIZE = 1024 * 1024  # 1 MB


def download_file(file_url: str, output_folder: str) -> Optional[str]:
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
            with requests.get(file_url, stream=True) as response:
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
                with open(out_file_temp, "wb") as target_file:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        target_file.write(chunk)
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

def download_cyg_antenna_patterns(antenna_patterns_folder_path=None):
    if antenna_patterns_folder_path is None:
        antenna_patterns_folder_path = os.path.join(os.environ["CYGNSS_PATH"], 'cygnss_antenna_patterns')
    if not os.path.isdir(antenna_patterns_folder_path):
        os.makedirs(antenna_patterns_folder_path)

    files_list = os.listdir(antenna_patterns_folder_path)
    if 'antennaRx_CYGNSS_Obs1_Nadir02_Starboard_processed' in files_list and 'antennaRx_CYGNSS_Obs1_Nadir01_Port_processed' in files_list:
        ant_ptrn_files_path = [os.path.join(antenna_patterns_folder_path, 'antennaRx_CYGNSS_Obs1_Nadir02_Starboard_processed'),
                               os.path.join(antenna_patterns_folder_path, 'antennaRx_CYGNSS_Obs1_Nadir01_Port_processed')]
        return ant_ptrn_files_path

    ant_ptrn_zip_path = os.path.join(antenna_patterns_folder_path, ANT_PTRN_URL.split('/')[-1])
    if not os.path.exists(ant_ptrn_zip_path):
        ant_ptrn_zip_path = download_file(ANT_PTRN_URL, antenna_patterns_folder_path)

    ant_ptrn_files_path = extract_ant_ptrn_zip(ant_ptrn_zip_path, antenna_patterns_folder_path)
    os.remove(ant_ptrn_zip_path)  # remove zip file
    return ant_ptrn_files_path


def extract_ant_ptrn_zip(zip_file_path, out_path):

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:

        files_list = zip_ref.namelist()
        extracted_files = list()
        for file_name in files_list:
            if file_name.endswith('processed'):
                zip_ref.extract(file_name, path=out_path)
                shutil.move(os.path.join(out_path, file_name), os.path.join(out_path, file_name.split(os.sep)[-1]))
                extracted_files.append(os.path.join(out_path, file_name.split(os.sep)[-1]))

    os.rmdir(os.path.join(out_path, file_name.split(os.sep)[0]))
    return extracted_files


if __name__ == '__main__':
    download_cyg_antenna_patterns()

