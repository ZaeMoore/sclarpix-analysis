import os
import shutil
import fire
import yaml
import pickle
import numpy as np
from collections import defaultdict

def rotate_pixel(pixel_pos, tile_orientation):
    return pixel_pos[0]*tile_orientation[2], pixel_pos[1]*tile_orientation[1]

def larpix_layout_to_dict(larpix_layout_name, geom_repo="builtin",
                          save_dict=True, dict_out=None):
    '''
        ------------- Note----------------
        The function asssumes each module has the same io configuration, which is currently used in the ndlar/2x2 simulation.
        Therefore, the dictionary is only for single module, and "get_raw_coord" deal with the coordinator of different modules.
        This might be updated in future iteration.
        ----------------------------------
        larpix_layout_name: the file name of the larpix layout configuration file (per module)
        geom_repo: the repository contains the larpix layout per module; by default, this function will use the geom repos that ship with the package, installed alongside the libraries
        save_dict: wether to save the dictionary to a pickle file; by default, if one choose not to save it, this funtion will the dictionary
        dict_out: the path to the output pickle file which contains the pixel readout dictionary
    '''

    if geom_repo == "builtin":
        geom_repo = os.path.join(os.path.dirname(__file__),
                                 "config_repo")

    larpix_geom_path = os.path.join(geom_repo, larpix_layout_name + ".yaml")
    with open(larpix_geom_path) as f_larpix:
        geometry_yaml = yaml.load(f_larpix, Loader=yaml.FullLoader)

    pixel_pitch = geometry_yaml['pixel_pitch']
    chip_channel_to_position = geometry_yaml['chip_channel_to_position']
    tile_orientations = geometry_yaml['tile_orientations']
    tile_positions = geometry_yaml['tile_positions']
    tile_indeces = geometry_yaml['tile_indeces']
    xs = np.array(list(chip_channel_to_position.values()))[:, 0] * pixel_pitch
    ys = np.array(list(chip_channel_to_position.values()))[:, 1] * pixel_pitch
    x_size = max(xs) - min(xs) + pixel_pitch
    y_size = max(ys) - min(ys) + pixel_pitch

    geometry = defaultdict(dict)
    
    for tile in geometry_yaml['tile_chip_to_io']:
        tile_orientation = tile_orientations[tile]

        for chip_channel in geometry_yaml['chip_channel_to_position']:
            chip = chip_channel // 1000
            channel = chip_channel % 1000
            try:
                io_group_io_channel = geometry_yaml['tile_chip_to_io'][tile][chip]
            except KeyError:
                continue

            io_group = io_group_io_channel // 1000 # io_group per module (not the real io_group)
            io_channel = io_group_io_channel % 1000
            x = chip_channel_to_position[chip_channel][0] * \
                pixel_pitch + pixel_pitch / 2 - x_size / 2
            y = chip_channel_to_position[chip_channel][1] * \
                pixel_pitch + pixel_pitch / 2 - y_size / 2
            
            x, y = rotate_pixel((x, y), tile_orientation)

            x += tile_positions[tile][2]
            y += tile_positions[tile][1]
            z = tile_positions[tile][0]
            direction = tile_orientations[tile][0]

            geometry[(io_group, io_channel, chip, channel)] = np.array([x, y, z, direction])

    # need to figure out what to do in case one doesn't have writting rights
    if save_dict:
        if dict_out is None:
            dict_path = os.path.join(geom_repo, "dict_repo")
            if not os.path.exists(dict_path):
                os.makedirs(dict_path)
            geom_dict_pkl_name = os.path.join(dict_path, larpix_layout_name + ".pkl")
        else:
            geom_dict_pkl_name = dict_out

        with open(geom_dict_pkl_name, 'wb') as outfile:
            pickle.dump(dict(geometry), outfile, protocol=pickle.HIGHEST_PROTOCOL)
    
    else:
        return dict(geometry)


if __name__ == "__main__":
    fire.Fire(larpix_layout_to_dict)
