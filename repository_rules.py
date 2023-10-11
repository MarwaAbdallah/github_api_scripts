import requests
import pandas as pd
import os
from dotenv import load_dotenv
import services.repos_service as rs
from github import Github
import time

''' 
    List all repository rules for every branch (not just protected)
    This is different from branch protection settings, as it is not set ta the same place
'''


base_url = "https://api.GitHub.com"
access_token= "token "+ str(os.getenv("GITHUB_TOKEN"))
headers = {
    'Authorization': str(access_token)
}





def rules_for_repository(repo_full_name):
    rules_for_branch_url = (
         base_url + "/repos/" + repo_full_name
         + "/rulesets"
        )

    try:
        response = requests.get(rules_for_branch_url, headers = headers).json()
        return response

    except requests.exceptions.RequestException as e: 
            print(" There was an issue loading"  + 
                    " rules from URL: " + rules_for_branch_url
                )


def main():
    startTime = time.time()
    df = pd.DataFrame()
    repos =  rs.list('input.csv')
    repos.drop([
         'Name',
         'Repo Languages',
         'Visibility',
         'Security And Analysis',
         'branches_url',
         'GHAS Default Config',
         'GHAS Language Config',
         'GHAS Schedule'
        ],
        inplace = True,
        axis = 1
    )

    for index, row in repos.iterrows():
        row['Rulesets'] = rules_for_repository(row['Full Name'])
        
        df = pd.concat(
            [
                df,
                row.to_frame().T
            ],
            axis = 0,
            ignore_index = True
        )

             
    executionTime = (time.time() - startTime)
    df.to_csv('output.csv', sep=',', encoding='utf-8',index=False)
    print('Execution time in seconds: ' + str(executionTime))


load_dotenv()
main()