#!/usr/bin/env python3
import os
import datetime
import datetime as dt
from typing import Union, Optional
from cygnsslib.cyg import land_flags_check
from osgeo import gdal, ogr
from cygnsslib.data_downloader.download_cygnss import get_cyg_file, download_cyg_files
from geographiclib.geodesic import Geodesic
from multiprocessing import Pool
from netCDF4 import Dataset
from tqdm import tqdm
import numpy as np
import pandas as pd


gdal.UseExceptions()


def roll_lon(val):
    if isinstance(val, np.ndarray):
        val[val > 180.0] += -360.0
    else:
        if val > 180.0:
            val += -360.0
    return val


def find_var_in_day(cygnss_l1_path: str, i_date: datetime.date, download_cygnss_data: bool, thresh_ddm_snr: float, ddm_quality_filter: int,
                    bbox: list, poly: ogr.Geometry, tf_poly: bool, lon_mode360: bool, ref_pos: Union[list, np.ndarray], radius: float, var_names,
                    tf_print_screen: bool, pbar: Optional[tqdm] = None):
    """
    Internal function for extracting CYGNSS variables of a specific day

    :param cygnss_l1_path: path of the main folder of CYGNSS L1 data (after the versions)
    :param i_date: date
    :param download_cygnss_data: download CYGNSS L1 data if they're not available?
    :param thresh_ddm_snr: DDM SNR threshold, above this value the DDM map image will be saved
    :param ddm_quality_filter: our quality flog number, above this number is low
    :param bbox:
    :param poly:
    :param tf_poly:
    :param lon_mode360:
    :param ref_pos:
    :param radius:
    :param var_names:
    :param tf_print_screen:
    :param pbar:
    :return:
    """
    geod = Geodesic.WGS84
    day_pnt_list_high = list()
    day_pnt_list_low = list()
    day = i_date.timetuple().tm_yday
    cyg_day_folder = os.path.join(cygnss_l1_path, f'{i_date.year:04d}', f'{day:03d}')
    for sc_num in np.arange(1, 9):
        if pbar is not None:
            pbar.update()
        filename = get_cyg_file(cyg_day_folder, sc_num)
        if filename is None and download_cygnss_data:
            file_name = download_cyg_files(i_date.year, day, sc_num, cygnss_l1_path=cygnss_l1_path)
            filename = None if (not file_name) else file_name[0]

        if filename is None:
            continue
        if tf_print_screen:
            print(filename)
        file_path = os.path.join(cyg_day_folder, filename)
        try:
            nc_file = Dataset(file_path)
            nc_file.set_auto_maskandscale(False)
            tsc = nc_file.time_coverage_start
            ddm_timestamp_utc = nc_file.variables["ddm_timestamp_utc"]
            sample = nc_file.variables["sample"]
            sc_num = nc_file.variables["spacecraft_num"]
            sp_lat = np.array(nc_file.variables["sp_lat"])
            sp_lon = np.array(nc_file.variables["sp_lon"])
            sp_inc_angle = nc_file.variables["sp_inc_angle"]
            ddm_snr = nc_file.variables["ddm_snr"]

        except (OSError, RuntimeError) as e:
            print(e)
            raise RuntimeError(f'Mostly, the file is damaged, try to re-download it again \n file path {file_path}')
        sp_lon_rolled = sp_lon[:]
        tf_rolled = sp_lon[:] > 180.0
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
                        qflags = np.array(nc_file.variables["quality_flags"][i_samp, i_chan])
                        sp_delay_row = int(nc_file.variables['brcs_ddm_peak_bin_delay_row'][i_samp, i_chan])
                        sp_dopp_col = int(nc_file.variables['brcs_ddm_peak_bin_dopp_col'][i_samp, i_chan])
                        qflags_msg_list, land_flag, our_flags = land_flags_check(qflags, nc_file.variables["sp_rx_gain"][i_samp, i_chan],
                                                                                 sp_delay_row, sp_dopp_col)

                        ddm_data = {var_: nc_file.variables[var_][i_samp, i_chan] for var_ in var_names}
                        timestamp_utc = np.timedelta64(int(ddm_timestamp_utc[i_samp] * 1e9), 'ns') + np.datetime64(tsc[:-1])
                        timestamp_utc_str = np.datetime_as_string(timestamp_utc)
                        ddm_metadata = {'ddm_timestamp_utc_str': timestamp_utc_str,
                                        'year': i_date.year,
                                        'day': day,
                                        'spacecraft_num': int(sc_num[0]),
                                        'channel': int(i_chan + 1),
                                        'sample_zero_based': int(i_samp),
                                        'sp_lat': float(sp_lat[i_samp, i_chan]),
                                        'sp_lon': float(sp_lon_rolled[i_samp, i_chan]),
                                        'sp_inc_angle': float(sp_inc_angle[i_samp, i_chan]),
                                        'ddm_snr': float(ddm_snr[i_samp, i_chan]),
                                        'DDM_quality': our_flags,
                                        'is_over_land': bool(land_flag),
                                        'quality_flags_msg': ', '.join(qflags_msg_list)}
                        ddm_data.update(ddm_metadata)
                        if ddm_snr[i_samp, i_chan] < thresh_ddm_snr or our_flags > ddm_quality_filter:
                            day_pnt_list_low.append(ddm_data)
                        else:
                            day_pnt_list_high.append(ddm_data)
        nc_file.close()
    return day_pnt_list_high, day_pnt_list_low


def _get_var_stat_from_poly_or_circle(date_list: list[dt.date], poly, ref_pos: Union[tuple[float], list[float]], radius: float,
                                      tf_poly: bool, var_list: list[str], thresh_ddm_snr: float, out_root: str, download_cygnss_data: bool,
                                      cygnss_l1_path: Optional[str], out_options: Optional[dict[str]]):

    if out_options is None:
        out_options = dict()
    plt_tag = out_options["plt_tag"] if ("plt_tag" in out_options) else ""
    tf_print_screen = not out_options['silent_mode'] if ("silent_mode" in out_options) else True
    pbar_tf = True if not tf_print_screen else False
    pbar_tf = out_options['progress_bar'] if ("progress_bar" in out_options) else pbar_tf
    parallel = out_options['multithreads'] if ('multithreads' in out_options) else False
    save_below_thresh = out_options['save_data_below_threshold'] if ('save_data_below_threshold' in out_options) else True
    ddm_quality_filter = out_options['ddm_quality_filter'] if ('ddm_quality_filter' in out_options) else 3
    sheet_save_type = 'xlsx'
    if 'sheet_type' in out_options:
        if out_options['sheet_type'].lower() == 'csv':
            sheet_save_type = 'csv'

    if cygnss_l1_path is None:
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
    var_stats_above_high = {var_: [0, np.inf, -np.inf, 0.0] for var_ in var_list}  # Num, min, max, mean
    var_stats_above_low = {var_: [0, np.inf, -np.inf, 0.0] for var_ in var_list}
    file_tag = os.path.basename(out_root)
    if parallel:
        # date_list_ = tqdm(date_list, total=len(date_list), desc='Searching CYGNSS files', unit='day') if pbar_tf else date_list
        pbar = None
        gdal.UseExceptions()

        with Pool() as pool:
            args = ((cygnss_l1_path, i_date, download_cygnss_data, thresh_ddm_snr, ddm_quality_filter, bbox, poly, tf_poly, lon_mode360,
                     ref_pos, radius, var_list, tf_print_screen, pbar) for i_date in date_list)
            results = [pool.apply_async(find_var_in_day, args=arg) for arg in args]
            if pbar_tf:
                pool_loop = tqdm(enumerate(results), desc=f'Stats: {file_tag}', unit='day', total=len(date_list))
            else:
                pool_loop = enumerate(results)
            for iresult, r in pool_loop:
                day_pnt_list_high, day_pnt_list_low = r.get()
                for point_list, var_stats in zip([day_pnt_list_high, day_pnt_list_low], [var_stats_above_high, var_stats_above_low]):
                    if point_list:
                        for var_name in var_list:
                            var_stats[var_name][0] += len(point_list)  # num
                            var_vals = np.array([ddm_data[var_name] for ddm_data in point_list])
                            min_val = np.min(var_vals)
                            max_val = np.max(var_vals)
                            sum_ = np.sum(var_vals)
                            var_stats[var_name][1] = np.minimum(var_stats[var_name][1], min_val)
                            var_stats[var_name][2] = np.maximum(var_stats[var_name][2], max_val)
                            var_stats[var_name][3] += sum_
        del args, day_pnt_list_high, day_pnt_list_low, pool_loop
    else:
        pbar = tqdm(total=len(date_list) * 8, desc=f'Stats: {file_tag}', unit='file') if pbar_tf else None
        for i_date in date_list:
            day_pnt_list_high, day_pnt_list_low = find_var_in_day(cygnss_l1_path, i_date, download_cygnss_data, thresh_ddm_snr, ddm_quality_filter,
                                                                  bbox, poly, tf_poly, lon_mode360, ref_pos, radius, var_list, tf_print_screen,
                                                                  pbar)
            for point_list, var_stats in zip([day_pnt_list_high, day_pnt_list_low], [var_stats_above_high, var_stats_above_low]):
                if point_list:
                    for var_name in var_list:
                        var_stats[var_name][0] += len(point_list)  # num
                        var_vals = np.array([ddm_data[var_name] for ddm_data in point_list])
                        min_val = np.min(var_vals)
                        max_val = np.max(var_vals)
                        sum_ = np.sum(var_vals)
                        var_stats[var_name][1] = np.minimum(var_stats[var_name][1], min_val)
                        var_stats[var_name][2] = np.maximum(var_stats[var_name][2], max_val)
                        var_stats[var_name][3] += sum_
    if pbar is not None:
        pbar.close()

    # Get average
    for var_stats in [var_stats_above_high, var_stats_above_low]:
        for var_name in var_list:
            if var_stats[var_name][0] > 0:
                var_stats[var_name][3] = var_stats[var_name][3] / var_stats[var_name][0]

    out_high_fp = out_root + '_high.csv'
    out_low_fp = out_root + '_low.csv'
    if not os.path.isdir(os.path.dirname(out_high_fp)):
        os.makedirs(os.path.dirname(out_high_fp))
    df_high = pd.DataFrame(var_stats_above_high, index=['Num', 'Min', 'Max', 'Mean']).T
    df_high.to_csv(out_high_fp)
    print(f'Stats high stave at {out_high_fp}')
    if save_below_thresh:
        df_low = pd.DataFrame(var_stats_above_low, index=['Num', 'Min', 'Max', 'Mean']).T
        df_low.to_csv(out_low_fp)
        print(f'Stats low stave at {out_low_fp}')


def get_var_stat_within_box_between_dates(st_date: dt.date, end_date: dt.date, lat_lim: Union[list[float], np.ndarray],
                                          lon_lim: Union[list[float], np.ndarray], var_list, out_folder_path: str, out_file_tag: str,
                                          thresh_ddm_snr: float = -9999.0, download_cygnss_data: bool = True,
                                          out_options: Optional[dict] = None, cygnss_l1_dir: Optional[str] = None):
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
    return _get_var_stat_from_poly_or_circle(date_list, poly, ref_pos, radius, tf_poly, var_list, thresh_ddm_snr, out_root, download_cygnss_data,
                                             cygnss_l1_dir, out_options)


def get_var_stat_within_radius(year: int, daylist: Union[list[int], np.ndarray, int], ref_pos: tuple[float, float], radius: float, var_list,
                               out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0, download_cygnss_data: bool = True,
                               out_options: Optional[dict] = None, cygnss_l1_dir: Optional[str] = None):

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
    return _get_var_stat_from_poly_or_circle(date_list, poly, ref_pos, radius, tf_poly, var_list, thresh_ddm_snr, out_root, download_cygnss_data,
                                             cygnss_l1_dir, out_options)


def get_var_stat_within_box(year: int, daylist: Union[list[int], np.ndarray, int], lat_lim: Union[list[float], np.ndarray],
                            lon_lim: Union[list[float], np.ndarray], var_list, out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0,
                            download_cygnss_data: bool = True, out_options: Optional[dict] = None, cygnss_l1_dir: Optional[str] = None):
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
    return _get_var_stat_from_poly_or_circle(date_list, poly, ref_pos, radius, tf_poly, var_list, thresh_ddm_snr, out_root, download_cygnss_data,
                                             cygnss_l1_dir, out_options)


def get_var_stat_within_radius_between_dates(st_date: dt.date, end_date: dt.date, ref_pos: tuple[float, float], radius: float, var_list: list[str],
                                             out_folder_path: str, out_file_tag: str, thresh_ddm_snr: float = -9999.0,
                                             download_cygnss_data: bool = True, out_options: Optional[dict] = None,
                                             cygnss_l1_dir: Optional[str] = None):
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

    return _get_var_stat_from_poly_or_circle(date_list, poly, ref_pos, radius, tf_poly, var_list, thresh_ddm_snr, out_root, download_cygnss_data,
                                             cygnss_l1_dir, out_options)


if __name__ == '__main__':
    lat = 32.5187357
    lon = -106.7434509
    margin = 0.2
    start_time = dt.date(2021, 1, 1)
    end_time = dt.date(2022, 1, 1)
    lat_ = [lat - margin, lat+margin]
    lon_ = [lon - margin, lon+margin]
    param_list = ['sp_inc_angle', 'tx_to_sp_range', 'rx_to_sp_range']
    get_var_stat_within_box_between_dates(start_time, end_time, lat_, lon_, param_list, 'test_output', 'z1_data',
                                          3, False)
