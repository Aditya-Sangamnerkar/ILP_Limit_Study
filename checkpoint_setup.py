import os
import sys
import json

SRC_DIR = "/mnt/ncsudrive/a/amsangam/ECE721/project1"

def __toolchain_setup():
	TOOLCHAIN_SETUP = "source /mnt/designkits/spec_2006_2017/O2_fno_bbreorder/activate.bash"
	os.system(TOOLCHAIN_SETUP)

def checkpoint_directory_name(checkpoint, version):
	return "-".join([checkpoint, version])

def benchmark_name(checkpoint):
	return ".".join(checkpoint.split(".")[0:2])

def __checkpoint_setup(checkpoint,config_type):
	
	# create directory for checkpoint
	checkpoint_dir = "{}/{}".format(SRC_DIR, checkpoint_directory_name(checkpoint, config_type))
	MKDIR = "mkdir {}".format(checkpoint_dir)
	os.system(MKDIR)

	# change working directory 
	os.chdir(checkpoint_dir)

	# create symbolic link for proxy kernel
	LN_KERNEL = "ln -s /mnt/designkits/spec_2006_2017/O2_fno_bbreorder/app_storage/pk"
	os.system(LN_KERNEL)
	
	# create symbolic link for 721sim
	LN_721SIM = "ln -s /mnt/ncsudrive/a/amsangam/ECE721/project1/721sim"
	os.system(LN_721SIM)

	# generate makefile
	benchmark = benchmark_name(checkpoint)
	GENERATE_MAKE = "atool-simenv mkgen {} --checkpoint {}".format(benchmark, checkpoint)
	print(GENERATE_MAKE)
	os.system(GENERATE_MAKE)

	return checkpoint_dir

def __run_sim(config, checkpoint_dir):

	# json file 
	os.chdir(SRC_DIR)
	with open('run_commands.json') as cmd_file:
		cmds = json.load(cmd_file)
	cmd_list = cmds[config]

	os.chdir(checkpoint_dir)
	for CMD in cmd_list:
		os.system(CMD)

def __extract_ipc(checkpoint_dir, config, checkpoint):
	
	# list files in checkpoint_dir
	os.chdir(checkpoint_dir)

	LS_FILES = "ls > files.txt"
	os.system(LS_FILES)

	# fetch stat files
	with open('files.txt') as files:
		file_list = files.readlines()

	stat_files = [file for file in file_list if 'stats' in file]

	ipc_rates = []
	for stat_file in stat_files:
		with open(stat_file.strip()) as data_file:
			data = data_file.readlines()
			for line in data:
				if('ipc_rate' in line):
					ipc_rates.append(line.split(":")[-1].strip())

	os.chdir(SRC_DIR)
	stats_csv = checkpoint+".csv"
	with open(stats_csv, 'a') as stat_csv:
		row = config + "," + ",".join(ipc_rates) + "\n"
		stat_csv.write(row)






def __run(checkpoint):	

	config_type = ['perfALL', 'realD$', 'realBP', 'noT$', 'realDISAMBIG', 'realDISAMBIGFlexible']


	for config in config_type:
		if(config == 'realDISAMBIGFlexible'):
			checkpoint_dir = __checkpoint_setup(checkpoint, config)
			__run_sim(config, checkpoint_dir)
			#__extract_ipc(checkpoint_dir, config, checkpoint)



if __name__ == '__main__':
	__run(sys.argv[1])



