import argparse
import json
import os
from collections import defaultdict
from cygnsslib.plotting import (plot_varying_sp_inc_angle, plot_varying_sc_az_angle, plot_reflectivity_x_az_lg_inc_angle,
                                plot_reflectivity_x_az_lg_sm, plot_reflectivity_vs_inc_angle_sm,
                                plot_reflectivity_vs_inc_angle_sm_all_az, plot_reflectivity_x_sm_lg_inc_angle_all_az)


# Function to load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to group data by 'smap_sm', 'sc_alt', 'sp_inc_angle', and 'sc_az_angle' values
def group_data(data):
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    for _, item in data.items():
        smap_sm = item.get('smap_sm')
        sc_alt = item.get('sc_alt')
        sp_inc_angle = item.get('sp_inc_angle')
        sc_az_angle = item.get('sc_az_angle')

        if smap_sm is not None and sc_alt is not None and sp_inc_angle is not None and sc_az_angle is not None:
            # Determine the smap_sm group by 0.05 ranges
            smap_sm_group = int(smap_sm // 0.05) * 0.05
            # Determine the sc_alt group by 10000 ranges
            sc_alt_group = int(sc_alt // 10000) * 10000
            # Determine the sp_inc_angle group by 5 ranges
            sp_inc_angle_group = int(sp_inc_angle // 5) * 5
            # Determine the sc_az_angle group by 5 ranges
            sc_az_angle_group = int(sc_az_angle // 5) * 5

            grouped_data[smap_sm_group][sc_alt_group][sp_inc_angle_group][sc_az_angle_group].append(item)

    return grouped_data



def analyze_cyg(json_fp, fig_save_types=None, db_lim=None, plt_options=None, separate_legend=False):
    default_plt_options = ['timeseries_az', 'timeseries_inc', 'inc_vs_sm_all_az', 'inc_vs_sm', 'az_lg_sm', 'az_lg_inc', 'sm_lg_inc']

    if plt_options is None:
        plt_options = default_plt_options
    else:
        for plt_opt in plt_options:
            if plt_opt not in default_plt_options:
                print(f'Not supported plot option: {plt_opt}, supported options: '+ ','.join(default_plt_options))

    if fig_save_types is None:
        fig_save_types = ['png']
    fn_split = os.path.basename(json_fp).split('_')
    _tag_idx = [idx for idx, txt in enumerate(fn_split) if txt.isnumeric()]
    if not _tag_idx:
        _tag_idx = 2
    else:
        _tag_idx = _tag_idx[0]
    img_tag = '_'.join(fn_split[:(_tag_idx+1)])

    data = load_json(json_fp)
    img_folder_name = f'{img_tag}_plots'
    folder_path = os.path.join(os.path.dirname(json_fp), img_folder_name)
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    grouped_data = group_data(data)
    if 'timeseries_inc' in plt_options:
        plot_varying_sp_inc_angle(grouped_data, folder_path, img_tag, fig_save_types)
    if 'timeseries_az' in plt_options:
        plot_varying_sc_az_angle(grouped_data, folder_path, img_tag, fig_save_types)
    if 'inc_vs_sm_all_az' in plt_options:
        plot_reflectivity_vs_inc_angle_sm_all_az(grouped_data, folder_path, img_tag, fig_save_types)
    if 'inc_vs_sm' in plt_options:
        plot_reflectivity_vs_inc_angle_sm(grouped_data, folder_path, img_tag, fig_save_types)
    if 'az_lg_sm' in plt_options:
        plot_reflectivity_x_az_lg_sm(grouped_data, folder_path, img_tag, fig_save_types, db_lim)
    if 'az_lg_inc' in plt_options:
        plot_reflectivity_x_az_lg_inc_angle(grouped_data, folder_path, img_tag, fig_save_types, db_lim, separate_legend)
    if 'sm_lg_inc' in plt_options:
        plot_reflectivity_x_sm_lg_inc_angle_all_az(grouped_data, folder_path, img_tag, fig_save_types, db_lim, separate_legend)


if __name__ == '__main__':
    opt_desc = ('1. timeseries_az: Plot timeseries of peak reflectivity, az_angle in legend \n '
                '2. timeseries_inc: Plot timeseries of peak reflectivity, incidence angle in legend \n '
                '3. inc_vs_sm_all_az: 2D plot of peak reflectivity, x-asis is soil moisture, y-axis incidence angle, all az angles in same plot \n '
                '4. inc_vs_sm: 2D plot of peak reflectivity, x-asis is soil moisture, y-axis incidence angle \n '
                '5. az_lg_sm: Plot peak reflectivity, x-asis azimuth angle, legend is soil moisture group \n '
                '6. az_lg_inc: Plot peak reflectivity, x-asis azimuth angle, legend is incidence angle group \n'
                '7. sm_lg_inc: Plot peak reflectivity, x-asis soil moisture, legend is incidence angle group, for all az angles')
    parser = argparse.ArgumentParser(description=f'Plot CYGNSS reflectivity: --plot_option \n {opt_desc}')
    parser.add_argument('input_path', type=str, help='Path to JSON file or folder has json files')
    parser.add_argument('--img_save_type', nargs='+', default=None, type=str, help='Image save types, i.e. png svg pdf')
    parser.add_argument('--dblim', nargs='+', default=None, type=int, help='dB lower and upper limit')
    parser.add_argument('--plot_option', nargs='+', default=None, type=str, help='Plotting options: timeseries_az, timeseries_inc, inc_vs_sm_all_az, inc_vs_sm, az_lg_sm, az_lg_inc, sm_lg_inc')
    parser.add_argument('--separate_legend', action='store_true', default=False, help='Plot legend in separate figure')

    args = parser.parse_args()
    if os.path.isdir(args.input_path):
        fps = [f.path for f in os.scandir(args.input_path) if f.name.endswith('.json')]
    else:
        fps = [args.input_path]
    for fp in fps:
        print(fp)
        analyze_cyg(fp, args.img_save_type, args.dblim, args.plot_option, args.separate_legend)
