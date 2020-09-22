#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import papermill
import itertools
import yaml
import os
import sys
import time
import json


# In[ ]:


# CONSTANTS
NOTEBOOKS_LIST_CONFIG_FILE = 'testnotebooks.yml'
global EXCEPTION_COUNT
EXCEPTION_COUNT = 0


# In[ ]:


# helper functions

def load_yaml(filepath):
    return yaml.load(open(filepath), Loader=yaml.FullLoader)

def get_param_combinations(config):
    keys = []
    values = []
    for key,val in config.items():
        keys.append(key)
        values.append(val) # Appends a list called val to values array.
    param_combinations = []
    for row in itertools.product(*values):
        param_combinations.append((dict(zip([k for k in keys], [v for v in row]))))
    return param_combinations

def run_notebook(nb_path, config_file_name):
    dir_name = os.path.dirname(nb_path)
    nb_name = os.path.basename(nb_path)
    output_nb_name = "output_{}.ipynb".format(time.time())
    os.chdir(dir_name)
    nb_test_config = load_yaml(config_file_name)
    for params in get_param_combinations(nb_test_config):        
        print("Executing: " + nb_name + " with parameters " + str(params))
        try:
            papermill.execute_notebook(nb_name, output_nb_name, parameters=params)
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            EXCEPTION_COUNT += 1
            


# In[ ]:


main_config = load_yaml(NOTEBOOKS_LIST_CONFIG_FILE)
print(main_config)


# In[ ]:


test_notebooks_list = main_config['notebooks']


# In[ ]:


ROOT = os.path.abspath('.')

for nb in test_notebooks_list:
    os.chdir(ROOT)
    print("Testing: {}".format(nb))
    config_file_name = main_config['configs'][nb]
    print("Config file: {}".format(config_file_name))
    run_notebook(nb, config_file_name)


# In[ ]:




