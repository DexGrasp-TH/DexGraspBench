rm -r output/debug_lz_gripper
python src/main.py hand=lz_gripper task=format exp_name=debug task.max_num=100 task.data_path=../bimanual_grasping/BODex/src/curobo/content/assets/output/sim_lz_gripper/tabletop/debug/graspdata
python src/main.py hand=lz_gripper task=eval exp_name=debug task.max_num=1000 setting=table
python src/main.py task=stat exp_name=debug
python src/main.py task=vusd exp_name=debug task.max_num=10
python src/main.py task=vobj exp_name=debug task.max_num=10
python src/main.py task=collect exp_name=debug
k.max_nu