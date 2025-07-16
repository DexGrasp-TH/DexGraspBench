rm -r output/debug_lz_gripper
python src/main.py hand=lz_gripper task=format exp_name=valid task.max_num=10000000 task.data_path=../bimanual_grasping/BODex/src/curobo/content/assets/output/sim_lz_gripper/tabletop/debug/graspdata
python src/main.py hand=lz_gripper task=eval exp_name=valid task.max_num=10000000 setting=tabletop task.valid_result_dir=../bimanual_grasping/BODex/src/curobo/content/assets/output/sim_lz_gripper/tabletop/valid_result/
python src/main.py task=stat hand=lz_gripper exp_name=valid
python src/main.py task=vusd hand=lz_gripper exp_name=valid task.max_num=10
python src/main.py task=vobj hand=lz_gripper exp_name=valid task.max_num=10
python src/main.py task=collect hand=lz_gripper exp_name=valid
