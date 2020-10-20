import requests
import tabulate 
from time import sleep  

TIME_TO_WAIT = 10

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
    # Print summary of tests ran.
    response = requests.get("http://localhost:5000/results").json()
    print(response)
    if response is not None:
        result = response['status']
        while result == "running":
            print("Checking in {0} seconds...".format(TIME_TO_WAIT))
            sleep(TIME_TO_WAIT)
            response = requests.get("http://localhost:5000/results").json()
            print(response)
            result = response['status']
#     SUCCESSES = 
#     print("Summary: {}/{} tests passed.".format(SUCCESSES.value, SUCCESSES.value + EXCEPTIONS.value))
#     print("Successful executions: ")
#     print_notebook_executions(SUCCESSFUL_EXECUTIONS)

#     # Throw exception if any test fails, so that the CodeBuild also fails.
#     if EXCEPTIONS.value > 0:
#         print("Failed executions: ")
#         print_notebook_executions(FAILED_EXECUTIONS)
#         raise Exception("Test did not complete successfully")

# print("Total time taken for tests: ")
# print(datetime.now() - startTime)

