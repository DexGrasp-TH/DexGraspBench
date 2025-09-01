import os
import multiprocessing
import logging
from glob import glob
import traceback

import numpy as np

from .eval_func import *


def safe_eval_one(params):
    input_npy_path, configs = params[0], params[1]
    # tabletopMocapEval(input_npy_path, configs).run()
    try:
        if configs.hand.mocap:
            eval_func_name = f"{configs.setting}MocapEval"
        else:
            eval_func_name = f"{configs.setting}ArmEval"
        eval(eval_func_name)(input_npy_path, configs).run()
        return
    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.warning(f"{error_traceback}")
        return


def task_eval(configs):
    assert (
        configs.task.simulation_metrics is not None
        or configs.task.analytic_fc_metrics is not None
        or configs.task.pene_contact_metrics is not None
    ), "You should at least evaluate one kind of metrics"
    input_path_lst = glob(os.path.join(configs.grasp_dir, "**/*.npy"), recursive=True)
    init_num = len(input_path_lst)

    if configs.skip:
        eval_path_lst = glob(os.path.join(configs.eval_dir, "**/*.npy"), recursive=True)
        eval_path_lst = [
            p.replace(configs.eval_dir, configs.grasp_dir) for p in eval_path_lst
        ]
        input_path_lst = list(set(input_path_lst).difference(set(eval_path_lst)))
    skip_num = init_num - len(input_path_lst)
    input_path_lst = sorted(input_path_lst)
    if configs.task.max_num > 0:
        input_path_lst = np.random.permutation(input_path_lst)[: configs.task.max_num]

    logging.info(
        f"Find {init_num} grasp data in {configs.grasp_dir}, skip {skip_num}, and use {len(input_path_lst)}."
    )

    if len(input_path_lst) == 0:
        return

    iterable_params = zip(input_path_lst, [configs] * len(input_path_lst))
    if configs.task.debug_viewer or configs.task.debug_render:
        for ip in iterable_params:
            safe_eval_one(ip)
    else:
        with multiprocessing.Pool(processes=configs.n_worker) as pool:
            result_iter = pool.imap_unordered(safe_eval_one, iterable_params)
            results = list(result_iter)

    grasp_lst = glob(os.path.join(configs.grasp_dir, "**/*.npy"), recursive=True)
    succ_lst = glob(os.path.join(configs.succ_dir, "**/*.npy"), recursive=True)
    eval_lst = glob(os.path.join(configs.eval_dir, "**/*.npy"), recursive=True)
    logging.info(
        f"Get {len(grasp_lst)} grasp data, {len(eval_lst)} evaluated, and {len(succ_lst)} succeeded in {configs.save_dir}"
    )
    logging.info(f"Finish evaluation")

    return


if __name__ == "__main__":
    import argparse
    from omegaconf import OmegaConf

    dic = {'skip': True, 'n_worker': 48, 'setting': 'tabletop', 'exp_name': 'debug', 'save_root': 'output', 'save_dir': 'output/debug_lz_gripper', 'grasp_dir': 'output/debug_lz_gripper/graspdata', 'eval_dir': 'output/debug_lz_gripper/evaluation', 'succ_dir': 'output/debug_lz_gripper/succgrasp', 'collect_dir': 'output/debug_lz_gripper/succ_collect', 'vusd_dir': 'output/debug_lz_gripper/vis_usd', 'vobj_dir': 'output/debug_lz_gripper/vis_obj', 'log_dir': 'output/debug_lz_gripper/log/eval/2025_07_15_06_22_31', 'task_name': 'eval', 'hand_name': 'lz_gripper', 'task': {'max_num': 1000, 'obj_mass': 0.1, 'miu_coef': [0.6, 0.02], 'debug_render': False, 'debug_viewer': False, 'debug_dir': 'output/debug_lz_gripper/debug', 'valid_result_dir': '../bimanual_grasping/BODex/src/curobo/content/assets/output/sim_lz_gripper/tabletop/valid_result', 'simulation_metrics': {'max_pene': 0.01, 'trans_thre': 0.05, 'angle_thre': 15}, 'analytic_fc_metrics': {'contact_tip_only': True, 'contact_threshold': 0.005, 'type': ['qp', 'qp_dfc', 'q1', 'tdg', 'dfc']}, 'pene_contact_metrics': {'contact_margin': 0.01, 'contact_threshold': 0.002}}, 'hand': {'xml_path': 'assets/hand/lz_gripper/lz_gripper_floating_wrist.xml', 'mocap': True, 'exclude_table_contact': None, 'color': [0.898039, 0.921569, 0.929412, 1.0], 'finger_prefix': ['thumb', 'index', 'middle', 'ring', 'little'], 'valid_body_name': ['base_link', 'thumb_link1', 'thumb_link2', 'thumb_link3', 'thumb_tip', 'index_link1', 'index_link2', 'index_tip', 'middle_link1', 'middle_link2', 'middle_tip', 'ring_link1', 'ring_link2', 'ring_tip', 'little_link1', 'little_link2', 'little_tip'], 'tip_body_name': ['thumb_tip', 'index_tip', 'middle_tip', 'ring_tip', 'little_tip']}}
    configs = OmegaConf.create(dic)

    task_eval(configs)
