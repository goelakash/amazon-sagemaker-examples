import boto3
from datetime import datetime
import json
from multiprocessing import Process
import paramiko
import requests
import tabulate 
from time import sleep

TIME_TO_WAIT = 30
UBUNTU_AMI = "ami-0c322afdce03ef272"
AL2_AMI = "ami-076199a859940b3a2"
KEY_PAIR_NAME = 'goelakas-rl'
SSH_TIMEOUT = 60
TEST_INSTANCE_TYPE = "c5.xlarge"
INSTANCE_NAME = "Integ_test_{0}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

USER_DATA = '''#!/bin/bash
git clone https://github.com/goelakash/amazon-sagemaker-examples.git
cd amazon-sagemaker-examples/reinforcement_learning
git checkout test-client-server
yes | pip install -r test_requirements.txt
export FLASK_APP=testserver.py
flask run --host=0.0.0.0'''

def run_ec2_server():
    ec2 = boto3.resource('ec2')
    new_instance = ec2.create_instances(
        ImageId=UBUNTU_AMI,
        InstanceType=TEST_INSTANCE_TYPE,
        # UserData=USER_DATA,
        MinCount=1,
        MaxCount=1,
        KeyName=KEY_PAIR_NAME,
        TagSpecifications=[{
            'ResourceType':'instance',
            'Tags':[
                {'Key':'Name',
                'Value':INSTANCE_NAME}]
            }]
        )
    instance = new_instance[0]
    instance.wait_until_running()
    instance.load()
    return instance

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

if __name__=="__main__":
    # Initialize EC2 server for running the tests
    print("Initializing EC2 server for running the tests...")
    instance = run_ec2_server()
    print("Waiting 5 minutes for the server to initialize")
    sleep(300)
    #Check if testing is done
    # (TODO: Move post number to env variables.)
    curl_url = "http://{0}:5000/results".format(instance.public_dns_name)
    response = requests.get(curl_url).json()
    print(response)
    if response is not None:
        status = response['status']
        while status == "running":
            print("Checking in {0} seconds...".format(TIME_TO_WAIT))
            sleep(TIME_TO_WAIT)
            response = requests.get(curl_url).json()
            print(response)
            status = response['status']
    instance.terminate_instances()
    passed = response['successful_executions']
    failures = response['failed_executions']


    # Print summary of tests ran.
    print("Summary: {}/{} tests passed.".format(len(passed), len(passed) + len(failures)))
    print("Successful executions: ")
    print_notebook_executions(json.loads(passed))

    # Throw exception if any test fails, so that the CodeBuild also fails.
    if len(failures) > 0:
        print("Failed executions: ")
        print_notebook_executions(json.loads(failures))
        raise Exception("Test did not complete successfully")
