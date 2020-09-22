#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import itertools
import json
import os
import pandas as pd
import papermill
import sys
from tabulate import tabulate
import time
import yaml


# In[ ]:


# CONSTANTS
NOTEBOOKS_LIST_CONFIG_FILE = 'testnotebooks.yml'
SUCCESSES = 0
EXCEPTIONS = 0
SUCCESSFUL_EXECUTIONS = []
FAILED_EXECUTIONS = []
CELL_EXECUTION_TIMEOUT_SECONDS = 600


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
    global SUCCESSES
    global EXCEPTIONS
    for params in get_param_combinations(nb_test_config):        
        print("Executing: " + nb_name + " with parameters " + str(params))
        try:
            papermill.execute_notebook(nb_name, output_nb_name, parameters=params, execution_timeout=CELL_EXECUTION_TIMEOUT_SECONDS)
            SUCCESSES += 1
            SUCCESSFUL_EXECUTIONS.append(dict({'notebook':nb_name, 'params':params}))
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            EXCEPTIONS += 1
            FAILED_EXECUTIONS.append(dict({'notebook':nb_name, 'params':params}))

def print_notebook_executions(nb_list_with_params):
    # This expects a list of dict type items.
    # E.g. [{'nb_name':'foo', 'params':'bar'}]
    if not nb_list_with_params:
        print("None")
        return
    vals = []
    for nb_dict in nb_list_with_params:
        val = []
        for k,v in nb_dict.items():
            val.append(v)
        vals.append(val)
    keys = [k for k in nb_list_with_params[0].keys()]
    print(tabulate(pd.DataFrame([v for v in vals], columns=keys), showindex=False))


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


print("Summary: {}/{} tests passed.".format(SUCCESSES, SUCCESSES + EXCEPTIONS))    
print("Successful executions: ")
print_notebook_executions(SUCCESSFUL_EXECUTIONS)
print("Failed executions: ")
print_notebook_executions(FAILED_EXECUTIONS)


# In[ ]:




