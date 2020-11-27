import sys, os, pprint

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, path)

# from haven.haven_jobs import slurm_manager as sm

  
# from haven import haven_chk as hc
# from haven import haven_results as hr
from haven import haven_utils as hu
import torch
import torchvision
import tqdm
import pandas as pd
import pprint
import itertools
import os
import pylab as plt
import time
import numpy as np
from torch.utils.data import RandomSampler, DataLoader
print()

import job_configs
# from haven_utils import file_utils




# Job status
# ===========
def get_job(job_id):
    """Get job information."""
    command = "scontrol show job %s" % job_id
    job_info = ''
    while True:
      try:
        job_info = hu.subprocess_call(command)
      except:
        print("scontrol time out and retry now")
        time.sleep(1)
        continue
      break
    return job_info
    

def get_jobs(account_id):
    # account_id = hu.subprocess_call('eai account get').split('\n')[-2].split(' ')[0]
    return 
           

# Job kill
# ===========
def kill_job(job_id):
    """Kill a job job until it is dead."""
    # todo: subprocess_call() time out?
    kill_command  = "scancel %s" % job_id
    info = hu.subprocess_call(kill_command)     # no return message after scancel
    return
import argparse


def get_existing_slurm_job_commands(exp_list, savedir_base):
    existing_job_commands = []
    for exp_dict in exp_list:
        exp_id = hu.hash_dict(exp_dict)
        savedir = os.path.join(savedir_base, exp_id)
        file_name = os.path.join(savedir, "job_dict.json")
        if not os.path.exists(file_name):
            continue
        job_dict = hu.load_json(file_name)
        job_id = job_dict["job_id"]
        job_status = hu.subprocess_call("scontrol show job %s" % job_id).split("JobState=")[1].split(" ")[0]
        if job_status == "RUNNING" or job_status == "PENDING":
            existing_job_commands += [job_dict["command"]]
        
    return existing_job_commands

def get_job_spec():
    # read slurm setting
    lines = "#! /bin/bash \n"
    lines += "#SBATCH --account=%s \n" % job_configs.ACCOUNT_ID
    for key in list(job_configs.JOB_CONFIG.keys()):
        lines += "#SBATCH --%s=%s \n" % (key, job_configs.JOB_CONFIG[key])
    return lines

def submit_job(command, savedir):
    # read slurm setting
    lines = "#! /bin/bash \n"
    # if job_config is not None:
    #     lines += "#SBATCH --account=%s \n" % job_configs.ACCOUNT_ID
    #     for key in list(job_config.keys()):
    #         lines += "#SBATCH --%s=%s \n" % (key, job_config[key])
    lines += "#SBATCH --account=%s \n" % job_configs.ACCOUNT_ID
    for key in list(job_configs.JOB_CONFIG.keys()):
      lines += "#SBATCH --%s=%s \n" % (key, job_configs.JOB_CONFIG[key])
    path_log = os.path.join(savedir, "logs.txt")
    path_err = os.path.join(savedir, "err.txt")
    lines += "#SBATCH --output=%s \n" % path_log
    lines += "#SBATCH --error=%s \n" % path_err
    
    lines += command

    file_name = os.path.join(savedir, "bash.sh")
    hu.save_txt(file_name, lines)
    # launch the exp
    submit_command = "sbatch %s" % file_name
    while True:
      try:
        job_id = hu.subprocess_call(submit_command).split()[-1]
      except:
        print("slurm time out and retry now")
        time.sleep(1)
        continue
      break

    # save the command and job id in job_dict.json
    job_dict = {
        "command": command,
        "job_id": job_id
    }
    hu.save_json(os.path.join(savedir, "job_dict.json"), job_dict)

    # delete the bash.sh
    os.remove(file_name)

    return job_id

if __name__ == "__main__":
  # task 1 - submit example job
  """
  Run echo 35 and forward the logs to <savedir>/logs.txt
  """
  command = 'echo 35'
  savedir = '/home/xhdeng/shared/results/test_slurm/example'
  job_id = submit_job(command, savedir)

  # task 2 - get job info as dict
  """
  Get job info as dict and save it as json in the directory specified below
  """
  job_info = get_job(job_id).replace('\n', '')
  job_info = {v.split('=')[0]:v.split('=')[1] for v in job_info.split(' ') if '=' in v }
  hu.save_json('/home/xhdeng/shared/results/test_slurm/example/job_info.json', job_info)

  # # task 3 - kill job
  # """
  # Kill job then gets its info as dict and save it as json in the directory specified below
  # it should say something like CANCELLED
  # """
  # kill_job(job_id)
  # job_info = get_job(job_id)
  # hu.save_json('/home/issamou/shared/results/slurm/example/job_info_dead.json', job_info)
  
  # # task 4 - get all jobs from an account as a list
  # """  
  # Get all jobs from an account as a list and save it in directory below
  # """
  # job_info_list = get_jobs(job_id)
  # hu.save_json('/home/issamou/shared/results/slurm/example/job_info_list.json', job_info_list)

  # # task 5 - run 10 jobs using threads
  # """
  # Use thee parallel threads from Haven and run these jobs in parallel
  # """
  # pr = hu.Parallel()
  # command_list = []

  # for i in range(1,20):
  #   command = 'echo %d' % i
  #   savedir = '/home/issamou/shared/results/slurm/example_%d' % i
  #   submit_job(command, savedir)
    
  #   pr.add(submit_job, command, savedir)

  # pr.run()
  # pr.close()
    

 