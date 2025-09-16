import os
from glob import glob
import multiprocessing
import logging

import numpy as np


def many_to_one(params):
    graspdata_path, save_path, succ_path = params[0], params[1], params[2]
    all_file_lst = os.listdir(graspdata_path)
    succ_file_lst = os.listdir(succ_path) if os.path.exists(succ_path) else []
    final_data_dict = {}
    succ_flag = []
    for i, f in enumerate(all_file_lst):
        data_dict = np.load(os.path.join(graspdata_path, f), allow_pickle=True).item()
        if i == 0:
            for k, v in data_dict.items():
                if "obj" not in k:
                    final_data_dict[k] = [v]
        else:
            for k, v in data_dict.items():
                if "obj" not in k:
                    final_data_dict[k].append(v)
        if f in succ_file_lst:
            succ_flag.append(True)
        else:
            succ_flag.append(False)
    for k in final_data_dict.keys():
        if k != "scene_path":
            final_data_dict[k] = np.stack(final_data_dict[k], axis=0)
        else:
            final_data_dict[k] = final_data_dict[k][0]
    final_data_dict['success'] = np.array(succ_flag)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    np.save(save_path, final_data_dict)
    return


def task_collect_with_succ(configs):
    all_path_lst = glob(os.path.join(configs.grasp_dir, "**/*.npy"), recursive=True)
    all_folder_lst = list(set([os.path.dirname(p) for p in all_path_lst]))

    logging.info(
        f"Get {len(all_path_lst)} success data and {len(all_folder_lst)} folder."
    )
    iter_param_lst = [
        (f, f.replace(configs.grasp_dir, configs.collect_dir) + ".npy", f.replace(configs.grasp_dir, configs.succ_dir))
        for f in all_folder_lst
    ]
    with multiprocessing.Pool(processes=configs.n_worker) as pool:
        result_iter = pool.imap_unordered(many_to_one, iter_param_lst)
        results = list(result_iter)
    return
