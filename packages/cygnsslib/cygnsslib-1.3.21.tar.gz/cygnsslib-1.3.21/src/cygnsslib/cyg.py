#!/usr/bin/env python3

#  FILE     cyg.py
#  DESCRIPTION
#           Tool set for working with CYGNSS data
#           See <https://bitbucket.org/usc_mixil/cygnss-library>
#  AUTHOR   Amer Melebari and James D. Campbell
#           Microwave Systems, Sensors and Imaging Lab (MiXiL)
#           University of Southern California
#  EMAIL    amelebar@usc.edu
#  CREATED  2018-04-06
#  Updated  2024-06-06 by Amer Melebari (amelebar@usc.edu)
#
#  Copyright 2024 University of Southern California
import os
import datetime
import datetime as dt
import matplotlib.pyplot as plt
import warnings
from typing import Union, Optional
import matplotlib.colors
from osgeo import gdal, ogr
from cygnsslib.data_downloader.download_cygnss import get_cyg_file, download_cyg_files, get_cyg_calibrated_rawif_file
from geographiclib.geodesic import Geodesic
from lxml import etree
from multiprocessing import Pool
from netCDF4 import Dataset
from tqdm import tqdm
import numpy as np
import pandas as pd
from cygnsslib.plotting import pwr2db_threshold, plot_single_ddm

gdal.UseExceptions()
qflag1_desc = ['ocean_poor_overall_quality',
               's_band_powered_up',
               'small_sc_attitude_err',
               'large_sc_attitude_err',
               'black_body_ddm',
               'ddmi_reconfigured',
               'spacewire_crc_invalid',
               'ddm_is_test_pattern',
               'channel_idle',
               'low_confidence_ddm_noise_floor',
               'sp_over_land',
               'sp_very_near_land',
               'sp_near_land',
               'large_step_noise_floor',
               'large_step_lna_temp',
               'direct_signal_in_ddm',
               'low_confidence_gps_eirp_estimate',
               'rfi_detected',
               'brcs_ddm_sp_bin_delay_error',
               'brcs_ddm_sp_bin_dopp_error',
               'neg_brcs_value_used_for_nbrcs',
               'gps_pvt_sp3_error',
               'sp_non_existent_error',
               'brcs_lut_range_error',
               'ant_data_lut_range_error',
               'bb_framing_error',
               'fsw_comp_shift_error',
               'low_quality_gps_ant_knowledge',
               'sc_altitude_out_of_nominal_range',
               'anomalous_sampling_period',
               'invalid_roll_state']
qflag2_desc = ['incorrect_ddmi_antenna_selection',
               'high_signal_noise',
               'noise_floor_cal_error',
               'sp_in_sidelobe',
               'negligible_nst_outage',
               'minor_nst_outage',
               'fatal_nst_outage',
               'low_zenith_ant_gain',
               'poor_bb_quality',
               'poor_quality_bin_ratio',
               'low_coherency_ratio',
               'land_poor_overall_quality',
               'sp_over_ocean',
               'sp_extremely_near_ocean',
               'sp_very_near_ocean',
               'land_obs_range_error']
def cyg_environ_check():
    if os.environ.get("CYGNSS_L1_PATH") is None:
        if os.environ.get('CYGNSS_DEFAULT_VER') is None or os.environ.get('CYGNSS_PATH') is None:
            raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")
        else:
            os.environ['CYGNSS_L1_PATH'] = os.path.join(os.environ['CYGNSS_PATH'], 'L1', os.environ['CYGNSS_DEFAULT_VER'])
    if os.environ.get('CYGNSS_PATH') is None:
        os.environ['CYGNSS_PATH'] = os.sep.join(os.environ.get("CYGNSS_L1_PATH").split(os.sep)[:-2])
    if os.environ.get('CYGNSS_DEFAULT_VER') is None:
        os.environ['CYGNSS_DEFAULT_VER'] = os.environ.get("CYGNSS_L1_PATH").split(os.sep)[-1]


def angle_with_north(reference_x, reference_y, reference_z, target_x, target_y, target_z):
    """
    Calculate the angle between the north direction and the line formed by two
    ECEF points with respect to the reference point.

    Parameters:
        reference_x (float): ECEF X-coordinate of the reference point.
        reference_y (float): ECEF Y-coordinate of the reference point.
        reference_z (float): ECEF Z-coordinate of the reference point.
        target_x (float): ECEF X-coordinate of the target point.
        target_y (float): ECEF Y-coordinate of the target point.
        target_z (float): ECEF Z-coordinate of the target point.

    Returns:
        float: Angle (in degrees) between the north direction and the line formed by the two points.
    """
    # Convert ECEF coordinates to geodetic coordinates
    reference_lat, reference_lon, _ = ecef_to_geodetic(reference_x, reference_y, reference_z)

    # transformer = pyproj.Transformer.from_crs(
    #     {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
    #     {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
    # )
    # lon1, lat1, alt1 = transformer.transform(reference_x, reference_y, reference_z, radians=False)
    target_lat, target_lon, _ = ecef_to_geodetic(target_x, target_y, target_z)

    # Calculate initial bearing from reference point to target point
    d_lon = target_lon - reference_lon
    y = np.sin(np.deg2rad(d_lon)) * np.cos(np.deg2rad(target_lat))
    x = np.cos(np.deg2rad(reference_lat)) * np.sin(np.deg2rad(target_lat)) - np.sin(np.deg2rad(reference_lat)) * np.cos(np.deg2rad(target_lat)) * np.cos(np.deg2rad(d_lon))
    initial_bearing = np.arctan2(y, x)

    # Convert bearing from radians to degrees
    initial_bearing = np.degrees(initial_bearing)

    # Normalize the bearing to range from 0 to 360 degrees
    initial_bearing = (initial_bearing + 360) % 360

    # Calculate angle between north direction and the bearing
    angle = (initial_bearing + 360 - 90) % 360  # Shift 90 degrees to align with north

    return initial_bearing


def ecef_to_geodetic(x, y, z):
    """
    Convert ECEF (Earth-Centered, Earth-Fixed) coordinates to geodetic coordinates.

    Parameters:
        x (float): ECEF X-coordinate.
        y (float): ECEF Y-coordinate.
        z (float): ECEF Z-coordinate.

    Returns:
        (float, float, float): Tuple containing geodetic latitude, longitude, and altitude (in degrees, degrees, meters).
    """
    # WGS84 parameters
    a = 6378137.0  # semi-major axis in meters
    b = 6356752.3  # semi-minor axis in meters
    e_sq = 6.69437999014e-3  # eccentricity squared

    # Calculate longitude
    lon = np.arctan2(y, x)

    # Calculate distance from Z-axis
    r = np.sqrt(x**2 + y**2)

    # Initial approximation of latitude
    lat_initial = np.arctan2(z, r)

    # Iterative calculation of latitude
    lat_prev = 2 * np.pi
    while np.abs(lat_prev - lat_initial) > 1e-6:
        lat_prev = lat_initial
        sin_lat = np.sin(lat_prev)
        N = a / np.sqrt(1 - e_sq * sin_lat**2)
        lat_initial = np.arctan2(z + e_sq * N * sin_lat, r)

    # Calculate altitude
    sin_lat = np.sin(lat_initial)
    N = a / np.sqrt(1 - e_sq * sin_lat**2)
    alt = r / np.cos(lat_initial) - N

    # Convert latitude and longitude to degrees
    lat = np.degrees(lat_initial)
    lon = np.degrees(lon)

    return lat, lon, alt


def roll_lon(val):
    if isinstance(val, np.ndarray):
        val[val > 180.0] += -360.0
    else:
        if val > 180.0:
            val += -360.0
    return val


def check_cyg_quality(qflags_list, sp_rx_gain=1, sp_delay_row=None, sp_dopp_col=None):
    """

    :param qflags_list:
    :type qflags_list: list of str
    :param sp_rx_gain: SP Rx gain
    :type sp_rx_gain: float
    :return:
    """
    lvl_1_flags = ['rfi_detected', 'direct_signal_in_ddm']
    lvl_2_flags = ['s_band_powered_up', 'small_sc_attitude_err', 'large_sc_attitude_err', 'black_body_ddm', 'ddmi_reconfigured',
                   'spacewire_crc_invalid', 'ddm_is_test_pattern', 'channel_idle', 'large_step_lna_temp', 'sp_non_existent_error']
    out_flag = 0 if sp_rx_gain > 0 else 2
    if sp_delay_row is not None:
        if sp_delay_row < 4 or sp_delay_row > 10:
            out_flag = 2
    if sp_dopp_col is not None:
        if sp_dopp_col < 3 or sp_dopp_col > 7:
            out_flag = 2

    for flag_msg in qflags_list:
        if out_flag == 2:  # if we found lvl 2 flag, exit the loop
            break
        for flag in lvl_2_flags:
            if flag in flag_msg:
                out_flag = 2
                break
        if out_flag != 2:
            for flag in lvl_1_flags:
                if flag in flag_msg:
                    out_flag = 1
                    break
    return out_flag
def check_cyg_quality_flags(qf1, qf2, snr, sp_rx_gain, inc_angle_deg, pekel_sp_water_flag, pekel_sp_water_percentage_5km, sp_in_ddm):


    flag1 = np.zeros(32, dtype=bool)
    flag2 = np.zeros(32, dtype=bool)
    sample_land_flags = []
    for bit_ in range(32):
        flag1[bit_] = np.bitwise_and(qf1, np.uint32(2 ** bit_))
        flag2[bit_] = np.bitwise_and(qf2, np.uint32(2 ** bit_))

    land_poor_qlty = False
    land_q1_bits = [2, 4, 5, 6, 7, 8, 9, 15, 16, 17, 22, 23, 25, 26, 27, 29, 30, 31]
    disp_q1_bits = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 22, 23, 25, 26, 27, 29, 30, 31]
    land_q2_bits = [1, 3, 4, 7, 8, 9, 13, 14, 16]
    disp_q2_bits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 16]

    for ibit, bit_val in enumerate(flag1):
        if bit_val and (ibit + 1) in disp_q1_bits:
            sample_land_flags.append(qflag1_desc[ibit])
            if bit_val and (ibit + 1) in land_q1_bits:
                land_poor_qlty = True
    for ibit, bit_val in enumerate(flag2):
        if bit_val and (ibit + 1) in disp_q2_bits:
            sample_land_flags.append(qflag2_desc[ibit])
        if bit_val and (ibit + 1) in land_q2_bits:
            land_poor_qlty = True
    if snr < 2.0:
        land_poor_qlty = True
        sample_land_flags.append('low_snr')
    if sp_rx_gain < 0.0:
        land_poor_qlty = True
        sample_land_flags.append('negative_sp_rx_gain')
    if inc_angle_deg > 65.0:
        land_poor_qlty = True
        sample_land_flags.append('high_inc_angle_deg')
    if pekel_sp_water_flag != 0:
        land_poor_qlty = True
        sample_land_flags.append('pekel_sp_water_flag')
    if pekel_sp_water_percentage_5km > 1:
        land_poor_qlty = True
        sample_land_flags.append('pekel_5km_water_flag')
    if not sp_in_ddm:
        land_poor_qlty = True
        sample_land_flags.append('sp_not_in_ddm')
    return land_poor_qlty, sample_land_flags

def land_flags_check(qflags, sp_rx_gain=1, sp_delay_row=None, sp_dopp_col=None):
    """
    Look up CYGNSS quality control flags for land applications
    :param qflags:
    :param sp_rx_gain: SP Rx gain
    :type sp_rx_gain: float
    :return: land_flag, qflags_tf, err_msg
    """

    err_msg_list = ['poor_overall_quality', 's_band_powered_up', 'small_sc_attitude_err', 'large_sc_attitude_err', 'black_body_ddm',
                    'ddmi_reconfigured', 'spacewire_crc_invalid', 'ddm_is_test_pattern', 'channel_idle', 'low_confidence_ddm_noise_floor',
                    'sp_over_land', 'sp_very_near_land', 'sp_near_land', 'large_step_noise_floor', 'large_step_lna_temp', 'direct_signal_in_ddm',
                    'low_confidence_gps_eirp_estimate', 'rfi_detected', 'brcs_ddm_sp_bin_delay_error', 'brcs_ddm_sp_bin_dopp_error',
                    'neg_brcs_value_used_for_nbrcs', 'gps_pvt_sp3_error', 'sp_non_existent_error', 'brcs_lut_range_error', 'ant_data_lut_range_error',
                    'bb_framing_error', 'fsw_comp_shift_error']
    qflags_tf = np.copy(qflags).astype(bool)
    qflags_tf.fill(False)
    # idx 0,10,11,12 are flags for land
    non_land_flag_idx = np.append(np.arange(1, 10), np.arange(13, 27)).astype(int)
    qflags_msg_list = list()
    for flag_idx in non_land_flag_idx:
        if qflags.size < 2 and (qflags & (1 << flag_idx)):
            qflags_msg_list.append(err_msg_list[flag_idx])

        qflags_tf = np.logical_or(qflags & (1 << flag_idx), qflags_tf)

    land_flag = np.array(qflags & (1 << 10), dtype=bool)  # report is the sp over land
    our_flags = check_cyg_quality(qflags_msg_list, sp_rx_gain, sp_delay_row, sp_dopp_col)
    if sp_rx_gain <= 0.0:
        qflags_msg_list.append('negative_sp_rx_gain')
    return qflags_msg_list, land_flag, our_flags


def write_sp_within_radius(cygnss_l1_dir: Optional[str], year: int, daylist: Union[list[int], np.ndarray, int], ref_pos: tuple[float, float],
                           radius: float, out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0,
                           download_cygnss_data: bool = True, out_options: Optional[dict] = None, search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    """
        This  search for all CYGNSS DDMs within radius from the ref_pos in the daylist time period. It exports the plots of the DDMs with SNR above
        thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param year: year number in 4 digits (ex. 2020) (you can't select multiple years for now
    :param daylist: list of days
    :param ref_pos: [lat,long]
    :param radius: radius of search in m
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param search_calib_rawif_sampling_rate: if value is not None, will search in calibrated RawIF data with sampling rate search_calib_rawif_sampling_rate
    :return: high SNR, low SNR, reference kml files paths

    """
    geod = Geodesic.WGS84
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)

    for angle in np.arange(0, 361, 1):
        poly_point = geod.Direct(ref_pos[0], ref_pos[1], angle, radius)
        geo_shape.AddPoint(poly_point["lon2"], poly_point["lat2"])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    tf_poly = False
    geo_shape = None

    year = int(year)
    if np.size(daylist) == 1:
        daylist = [int(daylist)]
    date_list = [dt.date(year, month=1, day=1) + dt.timedelta(days=int(iday) - 1) for iday in daylist]
    out_root = os.path.join(out_folder_path, out_file_tag)
    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, search_calib_rawif_sampling_rate)


def write_sp_within_box_between_dates(st_date: dt.date, end_date: dt.date, lat_lim: Union[list[float], np.ndarray],
                                      lon_lim: Union[list[float], np.ndarray], out_folder_path: str, out_file_tag: str,
                                      thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                                      out_options: Optional[dict] = None, cygnss_l1_dir: Optional[str] = None, search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)
    lat_lim = np.sort(lat_lim)
    lon_lim = np.sort(lon_lim)

    geo_shape.AddPoint(lon_lim[0], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[0])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    ref_pos = [0.0, 0.0]
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    ref_pos[1] = roll_lon(ref_pos[1])
    radius = 10
    tf_poly = True
    geo_shape = None

    num_days = (end_date - st_date).days + 1
    date_list = [st_date + dt.timedelta(days=iday) for iday in range(0, num_days)]
    out_root = os.path.join(out_folder_path, out_file_tag)
    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, search_calib_rawif_sampling_rate)


def write_sp_within_box(year: int, daylist: Union[list[int], np.ndarray, int], lat_lim: Union[list[float], np.ndarray],
                        lon_lim: Union[list[float], np.ndarray], out_folder_path: str, out_file_tag: str,
                        thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                        out_options: Optional[dict] = None, cygnss_l1_dir: Optional[str] = None, search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)
    lat_lim = np.sort(lat_lim)
    lon_lim = np.sort(lon_lim)

    geo_shape.AddPoint(lon_lim[0], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[0])
    geo_shape.AddPoint(lon_lim[1], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[1])
    geo_shape.AddPoint(lon_lim[0], lat_lim[0])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    ref_pos = [0.0, 0.0]
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    ref_pos[1] = roll_lon(ref_pos[1])
    radius = 10
    tf_poly = True
    geo_shape = None

    year = int(year)
    if np.size(daylist) == 1:
        daylist = [int(daylist)]
    date_list = [dt.date(year, month=1, day=1) + dt.timedelta(days=int(iday) - 1) for iday in daylist]
    out_root = os.path.join(out_folder_path, out_file_tag)
    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, search_calib_rawif_sampling_rate)


def write_sp_within_radius_between_dates(cygnss_l1_dir: Optional[str], st_date: dt.date, end_date: dt.date, ref_pos: tuple[float, float],
                                         radius: float, out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0,
                                         plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                                         out_options: Optional[dict] = None, search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    """
        This search for all CYGNSS DDMs within radius from the ref_pos from st_date to end_date. It exports the plots of the DDMs with SNR above
        thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param st_date: start date
    :param end_date: end date
    :param ref_pos: [lat,long]
    :param radius: radius of search in m
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param search_calib_rawif_sampling_rate: if value is not None, will search in calibrated RawIF data with sampling rate search_calib_rawif_sampling_rate
    :return: high SNR, low SNR, reference kml files paths
    """
    geod = Geodesic.WGS84
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)

    for angle in np.arange(0, 361, 1):
        poly_point = geod.Direct(ref_pos[0], ref_pos[1], angle, radius)
        geo_shape.AddPoint(poly_point["lon2"], poly_point["lat2"])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    tf_poly = False
    geo_shape = None

    num_days = (end_date - st_date).days + 1
    date_list = [st_date + dt.timedelta(days=iday) for iday in range(0, num_days)]
    out_root = os.path.join(out_folder_path, out_file_tag)

    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, search_calib_rawif_sampling_rate)


def write_sp_from_kml(cygnss_l1_dir: Optional[str], year: int, daylist: Union[list[int], np.ndarray], in_kml: str, out_folder_path: str,
                      out_file_tag: str, thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0, download_cygnss_data: bool = True,
                      out_options: Optional[dict] = None, search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    """
    This  search for all CYGNSS DDMs within the polygon in the in_kml within the daylist time period. It exports the plots of the DDMs with SNR above
    thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :type cygnss_l1_dir: str or None
    :param year: year number in 4 digits (ex. 2020) (you can't select multiple years for now
    :type year: int
    :param daylist: list of days
    :type daylist: list or np.array or int
    :param in_kml: name of the kml file that have the poly
    :type in_kml: str
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :type thresh_ddm_snr: float
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :type plt_thresh_noise: float
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :type download_cygnss_data: bool
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :type out_options: dict or None
    :param search_calib_rawif_sampling_rate: if value is not None, will search in calibrated RawIF data with sampling rate search_calib_rawif_sampling_rate

    :return: high SNR, low SNR, reference kml files paths
    """
    # Read polygon from input file and make longitude positive
    poly = get_poly(in_kml)
    # Find specular points inside polygon and write them to output
    ref_pos = [0.0, 0.0]
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    ref_pos[1] = roll_lon(ref_pos[1])

    radius = 10
    tf_poly = True
    year = int(year)
    if np.size(daylist) == 1:
        daylist = [int(daylist)]
    date_list = [dt.date(year, month=1, day=1) + dt.timedelta(days=int(iday) - 1) for iday in daylist]
    out_root = os.path.join(out_folder_path, out_file_tag)

    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, search_calib_rawif_sampling_rate)


def write_sp_from_kml_between_dates(cygnss_l1_dir: Optional[str], st_date: dt.date, end_date: dt.date, in_kml: str, out_folder_path: str,
                                    out_file_tag: str, thresh_ddm_snr: float = -9999.0, plt_thresh_noise: float = 1.0,
                                    download_cygnss_data: bool = True, out_options: Optional[dict] = None, search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    """
    This  search for all CYGNSS DDMs within the polygon in the in_kml within the daylist time period. It exports the plots of the DDMs with SNR above
    thesh_ddm_snr
    Note: The structure of the folders/files of  CYGNSS date need to be the same as the POO.DAC

    :param cygnss_l1_dir: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param st_date: start date
    :param end_date: end date
    :param in_kml: name of the kml file that have the poly
    :param out_folder_path: output folder path
    :param out_file_tag: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :param search_calib_rawif_sampling_rate: if value is not None, will search in calibrated RawIF data with sampling rate search_calib_rawif_sampling_rate
    :return: high SNR, low SNR, reference kml files paths

    """
    # Read polygon from input file and make longitude positive
    poly = get_poly(in_kml)
    # Find specular points inside polygon and write them to output
    ref_pos = [0.0, 0.0]
    ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
    ref_pos[1] = roll_lon(ref_pos[1])
    radius = 10
    tf_poly = True
    num_days = (end_date - st_date).days + 1
    date_list = [st_date + dt.timedelta(days=iday) for iday in range(num_days)]
    out_root = os.path.join(out_folder_path, out_file_tag)

    return _write_sp_from_poly_or_circle(cygnss_l1_dir, date_list, ref_pos, radius, thresh_ddm_snr, plt_thresh_noise, out_root, poly, tf_poly,
                                         download_cygnss_data, out_options, search_calib_rawif_sampling_rate)


def get_poly(in_kml):
    """
    get the polygon from the kml file and return a geometry class

    :param in_kml: kml file name
    :type in_kml: str
    :return: Geometry class in GDAL
    """
    dvr = ogr.GetDriverByName("KML")
    if not os.path.exists(in_kml):
        raise ImportError("Cannot find file {}".format(in_kml))

    ds_in = dvr.Open(in_kml)
    lyr = ds_in.GetLayer()
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    if geom.GetGeometryName() == 'MultiPolygon':
        geom.Polygonize()
        # multi  = ogr.Geometry(ogr.wkbMultiPolygon)
        # for i_g in range(geom.GetGeometryCount()):
        #     multi.AddGeometry(geom.GetGeometryRef(i_g))
        return geom.UnionCascaded()
    poly = ogr.Geometry(ogr.wkbPolygon)
    ring = geom.GetGeometryRef(0)
    for i_pt in range(ring.GetPointCount()):
        pt = ring.GetPoint(i_pt)
        lon_pos = pt[0]
        if lon_pos > 180:
            lon_pos += - 360
        ring.SetPoint(i_pt, lon_pos, pt[1])
    poly.AddGeometry(ring)
    ds_in = None
    return poly


def _write_sp_from_poly_or_circle(cygnss_l1_path: Optional[str], date_list: Union[list[dt.date], np.ndarray],
                                  ref_pos: Union[tuple[float, float], list[float]], radius: float, thresh_ddm_snr: float, plt_thresh_noise: float,
                                  out_root: str, poly, tf_poly: bool, download_cygnss_data: bool = True, out_options: Optional[dict] = None,
                                  search_calib_rawif_sampling_rate=None) -> tuple[str, str, str]:
    """

    :param search_calib_rawif_sampling_rate:
    :param cygnss_l1_path: the path of the main folder of CYGNSS L1 data (after the versions) (if None it uses os.environ.get("CYGNSS_L1_PATH"))
    :param date_list: list of dates
    :type date_list: list of dt.date or np.array of dt.date
    :param ref_pos: (lat,long)
    :param radius: radius of search in m
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM image will be saved
    :param plt_thresh_noise: noise threshold, each pixel in the DDM below this value will be replaced by this value
    :param out_root: tag for all the output files, ex: "out_root"_above_thresh.kml
    :param poly: Geometry class with the poly to search within
    :type poly: Geometry
    :param download_cygnss_data: download CYGNSS L1 data if they're not available ?
    :param out_options: currently we only implemented save_csv and save_ddm_img
    :return: high SNR, low SNR, reference kml files paths
    """
    sampling_rate = 0.5
    if search_calib_rawif_sampling_rate is not None:
        sampling_rate = search_calib_rawif_sampling_rate
    if out_options is None:
        out_options = dict()

    save_csv = out_options["save_csv"] if ("save_csv" in out_options) else False
    save_ddm_img = out_options["save_ddm_img"] if ("save_ddm_img" in out_options) else True
    plt_tag = out_options["plt_tag"] if ("plt_tag" in out_options) else ""
    plt_img_title = out_options['plt_img_title'] if ("plt_img_title" in out_options) else True
    img_save_type = out_options['img_save_type'] if ("img_save_type" in out_options) else ['png']
    tf_print_screen = not out_options['silent_mode'] if ("silent_mode" in out_options) else True
    pbar_tf = True if not tf_print_screen else False
    pbar_tf = out_options['progress_bar'] if ("progress_bar" in out_options) else pbar_tf
    parallel = out_options['multithreads'] if ('multithreads' in out_options) else False
    save_klm = out_options['save_klm'] if ('save_klm' in out_options) else True
    sp_high_color_name = out_options['sp_kml_color'] if ('sp_kml_color' in out_options) else 'lime'
    plt_reflectivity = out_options['plt_reflectivity'] if ('plt_reflectivity' in out_options) else False
    save_below_thresh = out_options['save_data_below_threshold'] if ('save_data_below_threshold' in out_options) else True
    ddm_quality_filter = out_options['ddm_quality_filter'] if ('ddm_quality_filter' in out_options) else 3
    save_cyg_var_keys = out_options['save_ddm_data_keys'] if ('save_ddm_data_keys' in out_options) else None
    sheet_save_type = 'xlsx'
    if 'sheet_type' in out_options:
        if out_options['sheet_type'].lower() == 'csv':
            sheet_save_type = 'csv'

    if cygnss_l1_path is None:
        if search_calib_rawif_sampling_rate is not None:
            try:
                cygnss_l1_path = os.path.join(os.environ['CYGNSS_PATH'], os.environ['CYGNSS_RAW_IF_FOLDER'])
            except KeyError as e:
                raise RuntimeError(f'Need to set environment variables $CYGNSS_PATH and $CYGNSS_RAW_IF_FOLDER or use cygnss_l1_path input parameter\n\n{e}')

        else:
            cygnss_l1_path = os.environ.get("CYGNSS_L1_PATH")
            if cygnss_l1_path is None:
                raise ValueError("$CYGNSS_L1_PATH environment variable need to be set, or use cygnss_l1_path input parameter")

    # Define bounding box containing circle of input radius for efficient data exclusion
    geod = Geodesic.WGS84
    if tf_poly:
        bbox = list(poly.GetEnvelope())
        ref_pos = [0.0, 0.0]
        ref_pos[1], ref_pos[0], *_ = poly.Centroid().GetPoint()
        ref_pos[1] = roll_lon(ref_pos[1])

        radius = 10
    else:
        g_n = geod.Direct(ref_pos[0], ref_pos[1], 0, radius)
        g_e = geod.Direct(ref_pos[0], ref_pos[1], 90, radius)
        g_s = geod.Direct(ref_pos[0], ref_pos[1], 180, radius)
        g_w = geod.Direct(ref_pos[0], ref_pos[1], 270, radius)
        bbox = [g_w["lon2"], g_e["lon2"], g_s["lat2"], g_n["lat2"]]
    lon_mode360 = False
    if bbox[0] > 180.0 or bbox[1] > 180.0:
        lon_mode360 = True
    bbox[0] = roll_lon(bbox[0])
    bbox[1] = roll_lon(bbox[1])
    # Define style tables
    sp_high_color_hex = matplotlib.colors.cnames.get(sp_high_color_name)
    if sp_high_color_hex is None:
        sp_high_color_hex = '#00FF00'
    # Open output
    klm_high_path = out_root + "_above_thresh.kml"
    klm_low_path = out_root + "_below_thresh.kml"
    out_folder = os.sep.join(out_root.split(os.sep)[:-1])

    out_sheet_name_list = [out_root + f"_{tag}_thresh" for tag in ['above', 'below']]
    fig_out_folder = os.path.join(out_folder, 'ddm_plots')
    if save_ddm_img:
        if not os.path.isdir(fig_out_folder):
            os.makedirs(fig_out_folder)

    # Iterate over selected CYGNSS datasets
    lookat_range = 35000  # m
    lookat_tilt = 0  # deg
    lyr_options = [f"LOOKAT_LONGITUDE={ref_pos[1]}",
                   f"LOOKAT_LATITUDE={(ref_pos[0])}",
                   f"LOOKAT_RANGE={lookat_range}",
                   f"LOOKAT_TILT={lookat_tilt}",
                   "FOLDER=YES"]

    # create in-situ kml file
    st_ref = ogr.StyleTable()
    st_ref.AddStyle("ref_normal", 'SYMBOL(c:#FFFF00,s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    st_ref.AddStyle("ref_highlight", 'SYMBOL(c:#FFFF00,s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    dvr = ogr.GetDriverByName("KML")
    out_ref = out_root + "_search_area.kml"
    if not os.path.isdir(os.path.dirname(out_ref)):
        os.makedirs(os.path.dirname(out_ref), exist_ok=True)
    ds_out_ref = dvr.CreateDataSource(out_ref)
    ds_out_ref.SetStyleTable(st_ref)
    lyr_name = "search_area"
    lyr = ds_out_ref.CreateLayer(lyr_name, geom_type=ogr.wkbLinearRing)
    lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
    feat = ogr.Feature(lyr.GetLayerDefn())
    feat.SetGeometry(poly)
    feat.SetField("Name", "search area")
    lyr.CreateFeature(feat)
    feat = None
    lyr = ds_out_ref.CreateLayer("In_Situ_Sensors", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
    feat = ogr.Feature(lyr.GetLayerDefn())
    pt_cur = ogr.Geometry(ogr.wkbPoint)
    pt_cur.AddPoint(float(ref_pos[1]), float(ref_pos[0]))
    feat.SetGeometry(pt_cur)
    feat.SetField("Name", "In-Situ Sensors")
    feat.SetStyleString("@ref")
    lyr.CreateFeature(feat)
    feat, lyr, ds_out_ref, st_ref, pt_cur = None, None, None, None, None
    file_tag = os.path.basename(out_root)

    if parallel:
        # date_list_ = tqdm(date_list, total=len(date_list), desc=f'Searching: {file_tag}', unit='day') if pbar_tf else date_list
        pbar = None
        gdal.UseExceptions()
        pnt_list_high = list()
        pnt_list_low = list()
        with Pool() as pool:
            args = ((cygnss_l1_path, i_date, download_cygnss_data, thresh_ddm_snr, ddm_quality_filter, bbox, poly, tf_poly, lon_mode360,
                     ref_pos, radius, tf_print_screen, save_ddm_img, img_save_type, plt_tag, plt_thresh_noise, plt_img_title, out_folder,
                     fig_out_folder, plt_reflectivity, None, search_calib_rawif_sampling_rate, save_cyg_var_keys) for i_date in date_list)

            results = pool.imap(_find_sp_in_day_wrap, args, chunksize=10)  # <-- preserves order
            # results = [pool.apply_async(_find_sp_in_day, args=arg) for arg in args]
            if pbar_tf:
                iteration_ = tqdm(enumerate(results), desc=f'Searching: {file_tag}', unit='day', total=len(date_list))
            else:
                iteration_ = enumerate(results)
            for iday, r in iteration_:
                day_pnt_list_high, day_pnt_list_low = r
                if day_pnt_list_high:
                    pnt_list_high += day_pnt_list_high
                if day_pnt_list_low:
                    pnt_list_low += day_pnt_list_low

        del args, day_pnt_list_high, day_pnt_list_low
    else:
        pbar = tqdm(total=len(date_list) * 8, desc=f'Searching: {file_tag}', unit='file') if pbar_tf else None
        pnt_list_high = list()
        pnt_list_low = list()
        for i_date in date_list:
            day_pnt_list_high, day_pnt_list_low = _find_sp_in_day(cygnss_l1_path, i_date, download_cygnss_data, thresh_ddm_snr, ddm_quality_filter,
                                                                  bbox, poly, tf_poly, lon_mode360, ref_pos, radius, tf_print_screen,
                                                                  save_ddm_img, img_save_type, plt_tag, plt_thresh_noise, plt_img_title,
                                                                  out_folder, fig_out_folder, plt_reflectivity, pbar, search_calib_rawif_sampling_rate,
                                                                  save_cyg_var_keys)
            if day_pnt_list_high:
                pnt_list_high += day_pnt_list_high
            if day_pnt_list_low:
                pnt_list_low += day_pnt_list_low
    if pbar is not None:
        pbar.close()
    if save_below_thresh:
        low_hex_color = '#FF0000'
        df_low = _export_sp_points(pnt_list_low, klm_low_path, lyr_options, sampling_rate, save_klm, low_hex_color, save_csv)
    else:
        df_low = None
    df_high = _export_sp_points(pnt_list_high, klm_high_path, lyr_options, sampling_rate, save_klm, sp_high_color_hex, save_csv)

    if save_klm:
        if pnt_list_high:
            add_look_at(klm_high_path, ref_pos, lookat_tilt, lookat_range)
        else:
            klm_high_path = None
        if save_below_thresh and pnt_list_low:
            add_look_at(klm_low_path, ref_pos, lookat_tilt, lookat_range)
        if not pnt_list_low:
            klm_low_path = None
    if save_csv:
        for df, fname in zip((df_high, df_low), out_sheet_name_list):
            if df is not None:
                if sheet_save_type == 'csv':
                    df.to_csv(f'{fname}.csv', index=False)
                else:
                    try:
                        df.to_excel(f'{fname}.xlsx', index=False)
                    except ValueError:
                        warnings.warn(f'cannot save data into xlsx file as the number of rows exceeded Excel limit. saving into {fname}.csv')
                        df.to_csv(f'{fname}.csv', index=False)

    return klm_high_path, klm_low_path, out_ref


def _export_sp_points(pnt_list: list[dict], klm_out_file_path: str, lyr_options, sampling_rate: float, save_klm: bool, sp_color_hex: str,
                      save_csv: bool) -> Optional[pd.DataFrame]:
    df_data = None
    if not pnt_list:
        print('No SP found in the selected region')
        return df_data
    if save_klm:
        dvr = ogr.GetDriverByName("LIBKML")
        st = ogr.StyleTable()
        st.AddStyle("sp_normal", f'SYMBOL(c:{sp_color_hex},s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/donut.png")')
        st.AddStyle("sp_highlight", f'SYMBOL(c:{sp_color_hex},s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/donut.png")')
        ds_out = dvr.CreateDataSource(klm_out_file_path)
        ds_out.SetStyleTable(st)

        for lyr_ in pnt_list:
            lyr = ds_out.CreateLayer(lyr_['lyr_name'], options=lyr_options, geom_type=ogr.wkbPoint)
            lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
            lyr.CreateField(ogr.FieldDefn("description", ogr.OFTString))
            for pnt_ in lyr_['points']:
                feat = ogr.Feature(lyr.GetLayerDefn())
                pt_cur = ogr.Geometry(ogr.wkbPoint)
                pt_cur.AddPoint(pnt_['ddm_data']['sp_lon'], pnt_['ddm_data']['sp_lat'])
                feat.SetField("Name", f"{pnt_['ddm_data']['sample_zero_based']}")
                feat.SetField('description', pnt_['dec'])
                feat.SetGeometry(pt_cur)
                feat.SetStyleString("@sp")
                lyr.CreateFeature(feat)
                feat = None
            lyr = None
        ds_out = None

    if save_csv:
        out_dic = dict()
        for keys in pnt_list[0]['points'][0]['ddm_data'].keys():
            out_dic[keys] = list()
        for lyr_ in pnt_list:
            for pnt_ in lyr_['points']:
                for keys, item in pnt_['ddm_data'].items():
                    out_dic[keys].append(item)
        # out_dic['sampling_rate'] = sampling_rate * np.ones(len(out_dic[list(out_dic.keys())[0]]))

        df_data = pd.DataFrame(out_dic)

    return df_data


def _find_sp_in_day_wrap(args):
    return _find_sp_in_day(*args)

def _find_sp_in_day(cygnss_l1_path: str, i_date: datetime.date, download_cygnss_data: bool, thresh_ddm_snr: float, ddm_quality_filter: int,
                    bbox: list, poly: ogr.Geometry, tf_poly: bool, lon_mode360: bool, ref_pos: Union[list, np.ndarray], radius: float,
                    tf_print_screen: bool, save_ddm_img: bool, img_save_type: Union[list, np.ndarray], plt_tag: str, plt_thresh_noise: float,
                    plt_img_title: True, out_folder: str, fig_out_folder: str, plt_reflectivity: bool = False, pbar: Optional[tqdm] = None,
                    rawif_sampling_rate=None, save_ddm_data_keys=None) -> tuple[list, list]:

    if rawif_sampling_rate is not None:
        is_calib_rawif = True
        data_sampling_rate = rawif_sampling_rate
    else:
        is_calib_rawif = False
        data_sampling_rate = None

    geod = Geodesic.WGS84
    day_pnt_list_high = list()
    day_pnt_list_low = list()
    day = i_date.timetuple().tm_yday
    cyg_day_folder = os.path.join(cygnss_l1_path, f'{i_date.year:04d}', f'{day:03d}')
    for sc_num in np.arange(1, 9):
        if pbar is not None:
            pbar.update()
        if is_calib_rawif:
            filename = get_cyg_calibrated_rawif_file(cyg_day_folder, sc_num, data_sampling_rate)
        else:
            filename = get_cyg_file(cyg_day_folder, sc_num)
        if filename is None and download_cygnss_data:
            file_name = download_cyg_files(i_date.year, day, sc_num, cygnss_l1_path=cygnss_l1_path)
            filename = None if (not file_name) else file_name[0]

        if filename is None:
            continue
        if tf_print_screen:
            print(filename)
        fullfile = os.path.join(cyg_day_folder, filename)
        try:
            nc_file = Dataset(fullfile)
            nc_file.set_auto_maskandscale(False)
            tsc = nc_file.time_coverage_start
            ddm_timestamp_utc = nc_file.variables["ddm_timestamp_utc"]
            sample = nc_file.variables["sample"]
            sc_num = nc_file.variables["spacecraft_num"]
            sp_lat = np.array(nc_file.variables["sp_lat"])
            sp_lon = np.array(nc_file.variables["sp_lon"])
            sp_inc_angle = nc_file.variables["sp_inc_angle"]
            ddm_snr = nc_file.variables["ddm_snr"]
            brcs = nc_file.variables["brcs"]
            sp_pos_x, sp_pos_y, sp_pos_z = nc_file.variables["sp_pos_x"], nc_file.variables["sp_pos_y"], nc_file.variables["sp_pos_z"]
            sc_pos_x, sc_pos_y, sc_pos_z = nc_file.variables["sc_pos_x"], nc_file.variables["sc_pos_y"], nc_file.variables["sc_pos_z"]
            tx_pos_x, tx_pos_y, tx_pos_z = nc_file.variables["tx_pos_x"], nc_file.variables["tx_pos_y"], nc_file.variables["tx_pos_z"]
            rx_to_sp_range, tx_to_sp_range = nc_file.variables["rx_to_sp_range"], nc_file.variables["tx_to_sp_range"]
            ddm_duration_t = np.round(ddm_timestamp_utc[1] - ddm_timestamp_utc[0], decimals=3)
            delay_scale = float(np.array(nc_file.variables['delay_resolution'])) / 0.255173
            if np.isclose(delay_scale, 1.0, rtol=1e-1, atol=1e-2):
                delay_scale = 1.0
            dopp_scale = float(np.array(nc_file.variables['dopp_resolution'])) / 500.0
            if np.isclose(dopp_scale, 1.0, rtol=1e-1, atol=1e-2):
                dopp_scale = 1.0

        except (OSError, RuntimeError) as e:
            print(e)
            raise RuntimeError(f'Mostly, the file is damaged, try to re-download it again \n file path {fullfile}')
        # n_delay = nc_file.dimensions["delay"].size
        # n_doppler = nc_file.dimensions["doppler"].size
        sp_lon_rolled = sp_lon[:]
        sp_lon_rolled[sp_lon[:] > 180.0] -= 360.0
        tf_in_box = (sp_lat[:] > bbox[2]) & (sp_lat[:] < bbox[3]) & (sp_lon_rolled > bbox[0]) & (sp_lon_rolled < bbox[1])
        tf_chan = np.sum(tf_in_box, axis=0) != 0

        for i_chan, tf_hit in enumerate(tf_chan):
            if tf_hit:
                tf_sel = tf_in_box[:, i_chan]
                sample_sel = sample[tf_sel]
                for i_samp in sample_sel:
                    if tf_poly:
                        pt_cur = ogr.Geometry(ogr.wkbPoint)
                        sel_sp_lon = sp_lon[i_samp, i_chan]
                        if lon_mode360 and sel_sp_lon < 0:
                            sel_sp_lon += 360.0
                        pt_cur.AddPoint(float(sel_sp_lon), float(sp_lat[i_samp, i_chan]))
                        sp_is_in_poly = pt_cur.Within(poly)
                        pt_cur = None
                    else:
                        g_dist = geod.Inverse(ref_pos[0], ref_pos[1], float(sp_lat[i_samp, i_chan]), float(sp_lon_rolled[i_samp, i_chan]))["s12"]
                        sp_is_in_poly = g_dist < radius
                        if sp_is_in_poly and tf_print_screen:
                            print(f'(dist={g_dist:2.0f} m)(ddm_snr={ddm_snr[i_samp, i_chan]:2.1f} dB)')

                    if sp_is_in_poly:
                        qflag1 = nc_file.variables["quality_flags"][i_samp, i_chan]
                        qflag2 = nc_file.variables["quality_flags_2"][i_samp, i_chan]
                        sp_rx_gain = nc_file.variables["sp_rx_gain"][i_samp, i_chan]
                        sel_sp_inc_angle = sp_inc_angle[i_samp, i_chan]
                        sel_ddm_snr = ddm_snr[i_samp, i_chan]
                        pekel_sp_water_flag = nc_file.variables["pekel_sp_water_flag"][i_samp, i_chan]
                        pekel_sp_water_percentage_5km = nc_file.variables["pekel_sp_water_percentage_5km"][i_samp, i_chan]
                        sp_delay_row = int(nc_file.variables['brcs_ddm_peak_bin_delay_row'][i_samp, i_chan])
                        sp_dopp_col = int(nc_file.variables['brcs_ddm_peak_bin_dopp_col'][i_samp, i_chan])
                        is_sp_in_ddm = False if np.abs(sp_delay_row) > 8 or np.abs(sp_dopp_col) > 5 else True
                        land_q_flag_tf,  land_flags_desc = check_cyg_quality_flags(qflag1, qflag2, sel_ddm_snr, sp_rx_gain,
                                                                                   sel_sp_inc_angle, pekel_sp_water_flag,
                                                                                   pekel_sp_water_percentage_5km, is_sp_in_ddm)
                        # Updated quality flag to use recommended flags for land application
                        # land_flags_desc, land_flag, our_flags = land_flags_check(qflag1, nc_file.variables["sp_rx_gain"][i_samp, i_chan],
                        #                                                          sp_delay_row, sp_dopp_col)

                        if ddm_snr[i_samp, i_chan] < thresh_ddm_snr or land_q_flag_tf:
                            pnt_list = day_pnt_list_low
                        else:
                            pnt_list = day_pnt_list_high

                        lyr_name = f"yr{i_date.year:04d}_day{day:03d}_sc{sc_num[0]}_ch{i_chan + 1}"
                        if not pnt_list or pnt_list[-1]['lyr_name'] != lyr_name:  # new lyr
                            pnt_list.append({'lyr_name': lyr_name, 'points': []})
                        timestamp_utc = np.timedelta64(int(ddm_timestamp_utc[i_samp] * 1e9), 'ns') + np.datetime64(tsc[:-1])
                        timestamp_utc_str = np.datetime_as_string(timestamp_utc)
                        description_field = [f'Year: {i_date.year:4d}', f'Day: {day:03d}', f'SC: {sc_num[0]:d}',
                                             f'Ch: {i_chan + 1:d}', f'Sample Id: {i_samp:d}',
                                             f'SNR: {ddm_snr[i_samp, i_chan]:.2f} dB',
                                             f'Incident Angle: {sp_inc_angle[i_samp, i_chan]:.2f} deg',
                                             f'Time form TSC: {int(ddm_timestamp_utc[i_samp] * 1e9):d} ns',
                                             f'DDM time: {timestamp_utc_str:s}', f'DDM quality flag: {land_q_flag_tf}']
                        ddm_save_var = {}
                        if save_ddm_data_keys is not None:
                            for _key in save_ddm_data_keys:
                                nc_var = np.array(nc_file.variables[_key])
                                if nc_var.ndim > 1:
                                    var_val_ = nc_var[i_samp, i_chan]
                                else:
                                    var_val_ = nc_var[i_samp]
                                ddm_save_var[_key] = var_val_
                        sc_az_angle = angle_with_north(sp_pos_x[i_samp, i_chan], sp_pos_y[i_samp, i_chan], sp_pos_z[i_samp, i_chan],
                                                       sc_pos_x[i_samp], sc_pos_y[i_samp], sc_pos_z[i_samp])
                        if sc_az_angle > 180.0:
                            sc_az_angle += -360.0
                        tx_az_angle = angle_with_north(sp_pos_x[i_samp, i_chan], sp_pos_y[i_samp, i_chan], sp_pos_z[i_samp, i_chan],
                                                       tx_pos_x[i_samp, i_chan], tx_pos_y[i_samp, i_chan], tx_pos_z[i_samp, i_chan])
                        if tx_az_angle > 180.0:
                            tx_az_angle += -360.0

                        ddm_data = {'ddm_timestamp_utc_str': timestamp_utc_str,
                                    'year': i_date.year,
                                    'day': day,
                                    'spacecraft_num': int(sc_num[0]),
                                    'channel': int(i_chan + 1),
                                    'sample_zero_based': int(i_samp),
                                    'sp_lat': float(sp_lat[i_samp, i_chan]),
                                    'sp_lon': float(sp_lon_rolled[i_samp, i_chan]),
                                    'sp_inc_angle': float(sp_inc_angle[i_samp, i_chan]),
                                    'ddm_snr': float(ddm_snr[i_samp, i_chan]),
                                    'ddm_int_time': float(ddm_duration_t),
                                    'land_quality_flag_tf': land_q_flag_tf,
                                    'sc_az_angle': sc_az_angle,
                                    'tx_az_angle': tx_az_angle}
                        if ddm_save_var is not None:
                            for _key, val_ in ddm_save_var.items():
                                ddm_data[_key] = val_
                        ddm_data['quality_flags_msg'] = ', '.join(land_flags_desc)

                        pnt_list[-1]['points'].append({'ddm_data': ddm_data, 'dec': ','.join(description_field)})
                        if ddm_snr[i_samp, i_chan] >= thresh_ddm_snr and save_ddm_img:  # Save plot of BRCS
                            if plt_reflectivity:
                                sc_pos = np.array([sc_pos_x[i_samp], sc_pos_y[i_samp], sc_pos_z[i_samp]])
                                tx_pos = np.array([tx_pos_x[i_samp, i_chan], tx_pos_y[i_samp, i_chan], tx_pos_z[i_samp, i_chan]])
                                ref_pos = np.array([sp_pos_x[i_samp, i_chan], sp_pos_y[i_samp, i_chan], sp_pos_z[i_samp, i_chan]])

                                ddm_ = brcs2reflectivity(brcs[i_samp, i_chan, :, :], tx_pos, sc_pos, ref_pos,
                                                         tx_to_sp_range[i_samp, i_chan], rx_to_sp_range[i_samp, i_chan])
                            else:
                                ddm_ = brcs[i_samp, i_chan, :, :]
                            if is_calib_rawif:  # DDM is flipped in RawIF
                                ddm_ = np.flip(ddm_, 0)
                            plt_cmax = None
                            try:
                                plot_cyg_brcs(ddm_, ddm_snr[i_samp, i_chan], sp_inc_angle[i_samp, i_chan], lyr_name,
                                              plt_tag, f"{i_samp}", img_save_type, fig_out_folder, tf_print_screen,
                                              plt_reflectivity, plt_cmax, delay_scale, dopp_scale, plt_img_title)
                            except Exception as e:
                                print(f'Exception while plotting {i_date.year}, {day}, SC {sc_num[0]}, Channel {i_chan+1} Sample {i_samp}', e)
        nc_file.close()
    return day_pnt_list_high, day_pnt_list_low


def brcs2reflectivity(brcs, tx_pos, rx_pos, ref_pos, tx_to_sp_range, rx_to_sp_range):
    # using range from cygnss file
    tx_sp_rng = tx_to_sp_range
    sp_rx_rng = rx_to_sp_range

    # if np.isnan(tx_sp_rng):
    #     tx_sp_rng = np.sqrt(np.sum((ref_pos - tx_pos) ** 2, axis=0))
    # if np.isnan(sp_rx_rng):
    #     sp_rx_rng = np.sqrt(np.sum((ref_pos - rx_pos) ** 2, axis=0))
    # this order prevent overflow issue
    factor = (tx_sp_rng + sp_rx_rng) ** 2 / tx_sp_rng ** 2 / sp_rx_rng ** 2 / (4.0 * np.pi)
    reflectivity = brcs * factor
    return reflectivity


def plot_cyg_brcs(brcs_sel: np.ndarray, ddm_snr: float, sp_inc_angle: str, lyr_name: str, plt_tag: str, pt_name: str,
                  img_save_type: Optional[list[str]], fig_out_folder: str, tf_print_screen: bool, reflectivity_tf: bool,
                  cbar_min_max: Optional[list[float]] = None, delay_scale=None, dopp_scale=None, plt_title_tf = True):
    brcs_db = pwr2db_threshold(brcs_sel)
    img_save_name = plt_tag + ('_' if plt_tag else '') + lyr_name + "_samp" + pt_name
    img_title = ''
    if plt_title_tf:
        img_title = f"ddm_snr = {ddm_snr:.2f} dB, inc = {sp_inc_angle:.1f} deg"
        img_title += f',\nSP Reflectivity = {np.max(brcs_db):.2g} dB' if reflectivity_tf else f', SP BRCS = {np.max(brcs_db):.2g} dBsm'
    cbar_title = 'Reflectivity [dB]' if reflectivity_tf else 'BRCS [dBsm]'
    fig = plot_single_ddm(brcs_db, img_title, img_save_name, fig_out_folder, fig_save_types=img_save_type, cbar_min_max=cbar_min_max,
                          cbar_title=cbar_title, delay_scale=delay_scale, dopp_scale=dopp_scale, plt_db_tf=True)
    if tf_print_screen:
        print(img_save_name)
    plt.close(fig)


def extract_parameters_frm_descrp(description_field):
    """

    :param description_field: the description field in the kml file
    :type description_field: str
    :return:
    :rtype: dic
    """
    if description_field == '':
        out_dic = None
    else:
        des_field_lwrcase = description_field.lower()
        year = int(des_field_lwrcase[des_field_lwrcase.find('year:'):].split(',')[0][5:])
        day = int(des_field_lwrcase[des_field_lwrcase.find('day:'):].split(',')[0][4:])
        sc_num = int(des_field_lwrcase[des_field_lwrcase.find('sc:'):].split(',')[0][3:])
        ch_id = int(des_field_lwrcase[des_field_lwrcase.find('ch:'):].split(',')[0][3:])
        samp_id = int(des_field_lwrcase[des_field_lwrcase.find('sample id:'):].split(',')[0][10:])
        snr = float(des_field_lwrcase[des_field_lwrcase.find('snr:'):].split(',')[0][4:-2])
        inc_ang = float(des_field_lwrcase[des_field_lwrcase.find('incident angle:'):].split(',')[0][15:-3])
        time_rltv_tsc_ns = int(des_field_lwrcase[des_field_lwrcase.find('time form tsc:'):].split(',')[0][14:-2])
        ddm_time_str = des_field_lwrcase[des_field_lwrcase.find('ddm time:'):].split(',')[0][10:]
        out_dic = {'year': year, 'day': day, 'sc_num': sc_num, 'ch_id': ch_id, 'samp_id': samp_id, 'snr': snr, 'inc_angl': inc_ang,
                   'time_rltv_tsc_ns': time_rltv_tsc_ns, 'sp_desc': description_field, 'ddm_time': ddm_time_str}

    return out_dic


def add_look_at(filename, ref_pos, lookat_tilt, lookat_range):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    doc = root.find('Document', namespaces=root.nsmap)
    look_at = etree.SubElement(doc, "LookAt", nsmap=root.nsmap)
    longitude = etree.SubElement(look_at, "longitude", nsmap=root.nsmap)
    longitude.text = f"{ref_pos[1]}"
    latitude = etree.SubElement(look_at, "latitude", nsmap=root.nsmap)
    latitude.text = f"{ref_pos[0]}"
    tilt = etree.SubElement(look_at, "tilt", nsmap=root.nsmap)
    tilt.text = f"{lookat_tilt}"
    rng = etree.SubElement(look_at, "range", nsmap=root.nsmap)
    rng.text = f"{lookat_range}"
    tree.write(filename, pretty_print=True, xml_declaration=True, encoding='UTF-8')


def create_centered_polygon(ref_pos, radius, out_kml, shape="circle"):
    """
    this function create a circle or a square in a kml file

    :param ref_pos: center of the polygon (lat,long)
    :type ref_pos: tuple or list
    :param radius: radius for the circle or half the length of the square [m]
    :type radius: float
    :param out_kml: name of the kml output file
    :type out_kml: str
    :param shape: only two shape are currently implemented; circle and square
    :type shape: str
    :return: file
    """
    geod = Geodesic.WGS84
    geo_shape = ogr.Geometry(ogr.wkbLinearRing)

    angle_inc_list = {"circle": 1, "square": 90}

    for angle in np.arange(0, 361, angle_inc_list[shape]):
        poly_point = geod.Direct(ref_pos[0], ref_pos[1], angle, radius)
        geo_shape.AddPoint(poly_point["lon2"], poly_point["lat2"])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(geo_shape)
    print(poly.Centroid())
    lyr_name = "{}_centered".format(shape)
    dvr = ogr.GetDriverByName("KML")
    ds_out = dvr.CreateDataSource(out_kml)
    lyr = ds_out.CreateLayer(lyr_name, geom_type=ogr.wkbLinearRing)
    feat = ogr.Feature(lyr.GetLayerDefn())
    feat.SetGeometry(poly)
    feat.SetField("Name", f"radius of {radius:.0f}")
    lyr.CreateFeature(feat)
    feat, lyr = None, None
    ds_out = None


def create_kml_from_list_points(loc_list, loc_names=None, out_kml="points.kml", lyr_name="points"):
    """
    create kml file from list of positions
    :param loc_list: array: Dim 0: points, dim 1: (lat,long)
    :type loc_list: ndarray
    :param loc_names: list of names, if None the name will be "Point No. d" starting from 1
    :type loc_names: list
    :param out_kml: out kml file name, default points.kml
    :type out_kml: str
    :param lyr_name: layer name, default: points
    :type lyr_name: str
    :return: void
    """

    st_ref = ogr.StyleTable()
    st_ref.AddStyle("ref_normal", 'SYMBOL(c:#FFFF00,s:1.0,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    st_ref.AddStyle("ref_highlight", 'SYMBOL(c:#FFFF00,s:1.3,id:"http://maps.google.com/mapfiles/kml/shapes/flag.png")')
    cnt_point = np.average(loc_list, axis=0)
    lookat_range = 35000  # m
    lookat_tilt = 0  # deg
    lyr_options = ["LOOKAT_LONGITUDE={}".format(cnt_point[1]),
                   "LOOKAT_LATITUDE={}".format(cnt_point[0]),
                   "LOOKAT_RANGE={}".format(lookat_range),
                   "LOOKAT_TILT={}".format(lookat_tilt),
                   "FOLDER=YES"]

    # Open output
    dvr = ogr.GetDriverByName("LIBKML")
    ds_out_ref = dvr.CreateDataSource(out_kml)
    ds_out_ref.SetStyleTable(st_ref)

    lyr = ds_out_ref.CreateLayer(lyr_name, options=lyr_options, geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
    point = ogr.Geometry(ogr.wkbPoint)

    for i_loc, loc in enumerate(loc_list):
        feat = ogr.Feature(lyr.GetLayerDefn())
        point.AddPoint(float(loc[1]), float(loc[0]))
        feat.SetGeometry(point)

        pt_name = "Point No. {:d}".format(i_loc + 1) if loc_names is None else "{}".format(loc_names[i_loc])
        feat.SetField("Name", pt_name)
        feat.SetStyleString("@ref")
        lyr.CreateFeature(feat)
        feat = None
    feat, lyr = None, None
    ds_out = None


def get_list_ddm_info_from_kml(in_kml: str) -> list[dict]:
    """
    get DDMs info from the kml file

    :param in_kml: kml file
    :type in_kml: str
    :return: list of dic that contains ddms info
    :rtype: list of dict
    """
    dvr = ogr.GetDriverByName("KML")
    kml_data = dvr.Open(in_kml, 0)
    if kml_data is None:
        raise FileExistsError(f"{in_kml:s} file doesn't exist")

    # get all the points in the KML file
    sp_loc_list = list()
    for lyr in kml_data:
        lyr_name = lyr.GetName()
        lyr_year = None
        lyr_day = None
        lyr_sc = None
        lyr_ch = None
        if 'yr' in lyr_name:
            lyr_year = int(lyr_name.split('yr')[1][0:4])
            lyr_day = int(lyr_name.split('day')[1][0:3])
            lyr_sc = int(lyr_name.split('sc')[1][0:1])
            lyr_ch = int(lyr_name.split('ch')[1][0:1])

        ddm_tag = lyr_name if ('Group'.lower() in lyr_name.lower()) else ''

        for idx, feat in enumerate(lyr):
            # feat_def = feat.GetFieldDefn()
            samp_id = int(feat.GetField('Name')) if str.isalnum(feat.GetField('Name')) else None

            geom = feat.GetGeometryRef()
            num_points = geom.GetPointCount()
            if num_points > 1:
                ValueError('expected one points in {:s}. got {:d}'.format(lyr_name, num_points))

            samp_loc = geom.GetPoint()
            ddm_info = extract_parameters_frm_descrp(feat.GetField('description'))
            if ddm_info is None:
                year = lyr_year
                day = lyr_day
                sc_num = lyr_sc
                ch_id = lyr_ch
                snr = None
                inc_ang = None
                time_rltv_tsc_ns = None
                ddm_time_str = None
            else:
                year = ddm_info['year']
                day = ddm_info['day']
                sc_num = ddm_info['sc_num']
                ch_id = ddm_info['ch_id']
                samp_id = ddm_info['samp_id']
                snr = ddm_info['snr']
                inc_ang = ddm_info['inc_angl']
                time_rltv_tsc_ns = ddm_info['time_rltv_tsc_ns']
                ddm_time_str = ddm_info['ddm_time']

            sp_loc_list.append({'year': year,
                                'day': day,
                                'sc_num': sc_num,
                                'ch_id': ch_id,
                                'samp_id': samp_id,
                                'lat': samp_loc[1],
                                'lon': samp_loc[0],
                                'snr': snr,
                                'inc_angl': inc_ang,
                                'time_rltv_tsc_ns': time_rltv_tsc_ns,
                                'sp_desc': feat.GetField('description'),
                                'ddm_time': ddm_time_str,
                                'tag': ddm_tag})
    return sp_loc_list


def group_sp_within_distance(in_kml, out_kml, max_dist, save_csv=False, sheet_type='xlsx'):
    """
    This function group the SP locations into groups, each group the distance between the points is less than the max distance

    :param in_kml: the kml file name from _write_sp_from_poly_or_circle() function
    :type in_kml: str
    :param out_kml: output kml file name
    :type out_kml: str
    :param max_dist: maximum distance between points within a group
    :type max_dist: float
    :param save_csv: export as a CSV file?
    :type save_csv: bool
    :param sheet_type: save the sheet in CSV or xls format? [CSV, xlsx]
    :type sheet_type: str
    :return:
    """
    sheet_type = 'csv' if sheet_type.lower() == 'csv' else 'xlsx'
    sp_loc_list = get_list_ddm_info_from_kml(in_kml)

    # find SP points within max_dist
    st_ref = ogr.StyleTable()
    for istyle in np.arange(1, 11):
        st_ref.AddStyle("pd{:d}_normal".format(istyle),
                        'SYMBOL(c:#00FF00,s:1.0,id:"http://maps.google.com/mapfiles/kml/paddle/{:d}.png")'.format(istyle))
        st_ref.AddStyle("pd{:d}_highlight".format(istyle),
                        'SYMBOL(c:#00FF00,s:1.3,id:"http://maps.google.com/mapfiles/kml/paddle/{:d}.png")'.format(istyle))

    dvr = ogr.GetDriverByName("LIBKML")
    ds_out_ref = dvr.CreateDataSource(out_kml)
    ds_out_ref.SetStyleTable(st_ref)
    lookat_range = 35000  # m
    lookat_tilt = 0  # deg
    # Open output
    df = None
    if save_csv:
        out_csv_file_name = f"{out_kml.split('.')[0]:s}.{sheet_type:s}"
        df = pd.DataFrame({'group_id': [],
                           'ddm_timestamp_utc_str': [],
                           'year': [],
                           'day': [],
                           'ddm_time_from_tsc_ns': [],
                           'sample_zero_based': [],
                           'spacecraft_num': [],
                           'channel': [],
                           'sp_lat': [],
                           'sp_lon': [],
                           'sp_inc_angle': [],
                           'ddm_snr': []})

    point = ogr.Geometry(ogr.wkbPoint)
    grp_id = 0  # first group start from 1
    geod = Geodesic.WGS84
    loc_in_grp = np.full(len(sp_loc_list), False,
                         dtype=bool)  # to prevent duplication of group, we're only considering level 2 don't come in multiple groups

    for idx1, sp_loc in enumerate(sp_loc_list[:-1]):
        if not loc_in_grp[idx1]:
            grp_exist = False
            loc_in_this_grp = np.full(len(sp_loc_list), False, dtype=bool)  # to prevent duplication in the group

            for idx2 in np.arange(idx1 + 1, len(sp_loc_list)):
                sp_loc2 = sp_loc_list[idx2]
                g_dist = geod.Inverse(sp_loc['lat'], sp_loc['lon'], sp_loc2['lat'], sp_loc2['lon'])
                if g_dist["s12"] <= max_dist:
                    if not grp_exist:
                        grp_exist = True
                        grp_id += 1
                        print(f'Group {grp_id:d}')
                        lyr_name = f'group: {grp_id:d}'
                        lyr_options = [f"LOOKAT_LONGITUDE={sp_loc['lon']}",
                                       f"LOOKAT_LATITUDE={sp_loc['lat']}",
                                       f"LOOKAT_RANGE={lookat_range}",
                                       f"LOOKAT_TILT={lookat_tilt}",
                                       f"FOLDER=YES"]

                        lyr = ds_out_ref.CreateLayer(lyr_name, options=lyr_options, geom_type=ogr.wkbPoint)
                        lyr.CreateField(ogr.FieldDefn("Name", ogr.OFTString))
                        lyr.CreateField(ogr.FieldDefn("description", ogr.OFTString))

                        # add the first point
                        feat = ogr.Feature(lyr.GetLayerDefn())
                        point.AddPoint(sp_loc['lon'], sp_loc['lat'])
                        feat.SetGeometry(point)
                        loc_in_grp[idx1] = True
                        loc_in_this_grp[idx1] = True
                        pt_name = "yr{:04d}_day{:03d}_sc{}_ch{}_samp{}".format(sp_loc['year'], sp_loc['day'], sp_loc['sc_num'], sp_loc['ch_id'],
                                                                               sp_loc['samp_id'])
                        feat.SetField("Name", pt_name)
                        feat.SetField("description", sp_loc['sp_desc'])
                        feat.SetStyleString("@pd{:d}".format(np.mod(grp_id - 1, 10) + 1))
                        lyr.CreateFeature(feat)
                        if save_csv:
                            df = pd.concat([df, pd.DataFrame({'group_id': [grp_id],
                                                              'ddm_timestamp_utc_str': [sp_loc['ddm_time']],
                                                              'year': [sp_loc['year']],
                                                              'day': [sp_loc['day']],
                                                              'ddm_time_from_tsc_ns': [sp_loc['time_rltv_tsc_ns']],
                                                              'sample_zero_based': [sp_loc['samp_id']],
                                                              'spacecraft_num': [sp_loc['sc_num']],
                                                              'channel': [sp_loc['ch_id']],
                                                              'sp_lat': [sp_loc['lat']],
                                                              'sp_lon': [sp_loc['lon']],
                                                              'sp_inc_angle': [sp_loc['inc_angl']],
                                                              'ddm_snr': [sp_loc['snr']]})], ignore_index=True)
                    loc_in_grp[idx2] = True
                    if not loc_in_this_grp[idx2]:
                        point.AddPoint(sp_loc2['lon'], sp_loc2['lat'])
                        feat.SetGeometry(point)

                        pt_name = "yr{:04d}_day{:03d}_sc{}_ch{}_samp{}".format(sp_loc2['year'], sp_loc2['day'], sp_loc2['sc_num'], sp_loc2['ch_id'],
                                                                               sp_loc2['samp_id'])
                        feat.SetField("Name", pt_name)
                        feat.SetField("description", sp_loc2['sp_desc'])
                        feat.SetStyleString("@pd{:d}".format(np.mod(grp_id - 1, 10) + 1))
                        lyr.CreateFeature(feat)
                        if save_csv:
                            df = pd.concat([df, pd.DataFrame({'group_id': [grp_id],
                                                              'ddm_timestamp_utc_str': [sp_loc['ddm_time']],
                                                              'year': [sp_loc['year']],
                                                              'day': [sp_loc['day']],
                                                              'ddm_time_from_tsc_ns': [sp_loc['time_rltv_tsc_ns']],
                                                              'sample_zero_based': [sp_loc['samp_id']],
                                                              'spacecraft_num': [sp_loc['sc_num']],
                                                              'channel': [sp_loc['ch_id']],
                                                              'sp_lat': [sp_loc['lat']],
                                                              'sp_lon': [sp_loc['lon']],
                                                              'sp_inc_angle': [sp_loc['inc_angl']],
                                                              'ddm_snr': [sp_loc['snr']]})], ignore_index=True)

                        print('    distance to ref. point: {:f} m'.format(g_dist["s12"]))
                        loc_in_this_grp[idx2] = True

                    for idx3 in np.arange(idx1 + 1, len(sp_loc_list)):
                        if not loc_in_this_grp[idx3] and idx3 != idx2:
                            sp_loc3 = sp_loc_list[idx3]
                            g_dist = geod.Inverse(sp_loc2['lat'], sp_loc2['lon'], sp_loc3['lat'], sp_loc3['lon'])
                            if g_dist["s12"] <= max_dist:
                                point.AddPoint(sp_loc3['lon'], sp_loc3['lat'])
                                feat.SetGeometry(point)

                                pt_name = f"yr{sp_loc3['year']:04d}_day{sp_loc3['day']:03d}_sc{sp_loc3['sc_num']}_ch{sp_loc3['ch_id']}" \
                                          f"_samp{sp_loc3['samp_id']}"
                                feat.SetField("Name", pt_name)
                                feat.SetField("description", sp_loc3['sp_desc'])
                                feat.SetStyleString("@pd{:d}".format(np.mod(grp_id - 1, 10) + 1))
                                lyr.CreateFeature(feat)
                                if save_csv:
                                    df = pd.concat([df, pd.DataFrame({'group_id': [grp_id],
                                                                      'ddm_timestamp_utc_str': [sp_loc['ddm_time']],
                                                                      'year': [sp_loc['year']],
                                                                      'day': [sp_loc['day']],
                                                                      'ddm_time_from_tsc_ns': [sp_loc['time_rltv_tsc_ns']],
                                                                      'sample_zero_based': [sp_loc['samp_id']],
                                                                      'spacecraft_num': [sp_loc['sc_num']],
                                                                      'channel': [sp_loc['ch_id']],
                                                                      'sp_lat': [sp_loc['lat']],
                                                                      'sp_lon': [sp_loc['lon']],
                                                                      'sp_inc_angle': [sp_loc['inc_angl']],
                                                                      'ddm_snr': [sp_loc['snr']]})], ignore_index=True)
                                loc_in_this_grp[idx3] = True
                                print(f'    distance to ref. point: {g_dist["s12"]:f} m')

    ds_out_ref = None
    if save_csv:
        if sheet_type == 'csv':
            df.to_csv(out_csv_file_name, index=False)
        else:
            df.to_excel(out_csv_file_name, index=False)


def plot_brcs(cygnss_l1_dir, year, day, sc_num, ch_num, samp_num, tag_png, tag_title):
    """
    plotting BRCS of DDM,
    Note: this function is not kept up to date
    :param cygnss_l1_dir:
    :param year:
    :param day:
    :param sc_num:
    :param ch_num:
    :param samp_num:
    :param tag_png:
    :param tag_title:
    :return:
    """
    dirname = os.path.join(cygnss_l1_dir, f'{year:04d}', f'{day:03d}')
    assert os.path.isdir(dirname), f"Cannot find dir {dirname}"
    filelist = [x for x in os.listdir(dirname) if x.endswith('.nc')]
    filelist.sort()
    for filename in filelist:
        fullfile = os.path.join(dirname, filename)
        nc_file = Dataset(fullfile)
        nc_file.set_auto_maskandscale(False)
        nc_sc_num = nc_file.variables["spacecraft_num"]
        sc_num_sel = nc_sc_num[0]
        if sc_num_sel == sc_num:
            sp_lat = nc_file.variables["sp_lat"]
            sp_lon = nc_file.variables["sp_lon"]
            sp_inc_angle = nc_file.variables["sp_inc_angle"]
            brcs_ddm_peak_bin_delay_row = nc_file.variables["brcs_ddm_peak_bin_delay_row"]
            brcs_ddm_peak_bin_dopp_col = nc_file.variables["brcs_ddm_peak_bin_dopp_col"]
            sv_num = nc_file.variables["sv_num"]
            track_id = nc_file.variables["track_id"]
            rx_to_sp_range = nc_file.variables["rx_to_sp_range"]
            tx_to_sp_range = nc_file.variables["tx_to_sp_range"]
            brcs = nc_file.variables["brcs"]
            area_e = nc_file.variables["eff_scatter"]
            n_delay = nc_file.dimensions["delay"].size
            n_doppler = nc_file.dimensions["doppler"].size
            sp_lat_sel = sp_lat[samp_num, ch_num - 1]
            sp_lon_sel = sp_lon[samp_num, ch_num - 1]
            if sp_lon_sel >= 180.0:
                sp_lon_sel -= 360
            i_delay = brcs_ddm_peak_bin_delay_row[samp_num, ch_num - 1]
            i_dopp = brcs_ddm_peak_bin_dopp_col[samp_num, ch_num - 1]
            brcs_sel = brcs[samp_num, ch_num - 1, :, :]
            area_e_sel = area_e[samp_num, ch_num - 1, :, :]
            # el_obj = srtm.get_data()
            # el_meters = el_obj.get_elevation(sp_lat_sel,sp_lon_sel)
            el_meters = None
            if el_meters is None:
                print("Couldn't get the elevation, it's set to 0, mostly its because you're outside the range of srtm.")
                el_meters = 0

            print("Latitude: {0}, Longitude: {1}, Elevation: {2}".format(sp_lat_sel, sp_lon_sel, el_meters))
            sp_lat_dms = gdal.DecToDMS(float(sp_lat_sel), "Lat")
            sp_lon_dms = gdal.DecToDMS(float(sp_lon_sel), "Long")
            rx_to_sp_range_sel = rx_to_sp_range[samp_num, ch_num - 1]
            tx_to_sp_range_sel = tx_to_sp_range[samp_num, ch_num - 1]
            ratio = float(tx_to_sp_range_sel) / (tx_to_sp_range_sel + rx_to_sp_range_sel)
            factor = 4 * np.pi * (rx_to_sp_range_sel * ratio) ** 2
            if i_delay != -99 and i_dopp != -99:
                brcs_peak = brcs_sel[i_delay, i_dopp]
                area_peak = area_e_sel[i_delay, i_dopp]
                area_sp = area_e_sel[8, 5]
            else:
                brcs_peak = 0
                area_peak = 0
                area_sp = 0
            fresnel = brcs_peak / factor
            fig, ax = plt.subplots()
            plt.imshow(brcs_sel, extent=[0.5, n_doppler + 0.5, n_delay + 0.5, 0.5])
            plt.colorbar(shrink=0.9)
            title_str = "BRCS [m^2]: {}\n" \
                        "yr={}, day={:03d}, sc={}, ch={}, samp={}\n" \
                        "sp_lat={}, sp_lon={}\n" \
                        "el={:.0f} m, sp_inc={:.1f} deg, sv_num={}\n" \
                        "pk_delay={}, pk_dopp={}, Reflectivity={:.2g}\n"
            plt.title(title_str.format(tag_title, year, day, sc_num, ch_num, samp_num,
                                       sp_lat_dms, sp_lon_dms,
                                       el_meters, sp_inc_angle[samp_num, ch_num - 1], sv_num[samp_num, ch_num - 1],
                                       i_delay + 1, i_dopp + 1, fresnel))
            plt.xlabel('Doppler Bin')
            plt.ylabel('Delay Bin')
            plt.xticks(range(1, n_doppler + 1))
            plt.yticks(range(1, n_delay + 1))
            out_png = "{}_brcs_yr{}_day{:03d}_sc{}_ch{}_samp{}".format(tag_png, year, day, sc_num, ch_num, samp_num)
            fig.savefig(out_png, bbox_inches='tight')
            plt.close(fig)

            fig, ax = plt.subplots()
            plt.imshow(area_e_sel, extent=[0.5, n_doppler + 0.5, n_delay + 0.5, 0.5])
            plt.colorbar(shrink=0.9)
            title_str = "Effective Area [m^2]: {}\n" \
                        "yr={}, day={:03d}, sc={}, ch={}, samp={}\n" \
                        "sp_lat={}, sp_lon={}\n" \
                        "el={:.0f} m, sp_inc={:.1f} deg, sv_num={}\n" \
                        "pk_delay={}, pk_dopp={}, A_pk={:.2g}, A_sp={:.2g}\n"
            plt.title(title_str.format(tag_title, year, day, sc_num, ch_num, samp_num,
                                       sp_lat_dms, sp_lon_dms,
                                       el_meters, sp_inc_angle[samp_num, ch_num - 1], sv_num[samp_num, ch_num - 1],
                                       i_delay + 1, i_dopp + 1, area_peak, area_sp))
            plt.xlabel('Doppler Bin')
            plt.ylabel('Delay Bin')
            plt.xticks(range(1, n_doppler + 1))
            plt.yticks(range(1, n_delay + 1))
            out_png = "{}_area_yr{}_day{:03d}_sc{}_ch{}_samp{}".format(tag_png, year, day, sc_num, ch_num, samp_num)
            fig.savefig(out_png, bbox_inches='tight')
            plt.close(fig)
