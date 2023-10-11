import requests
import pandas as pd
import os
from dotenv import load_dotenv
from github import Github
import time

''' 
    TODO:
    - code scanning, when an advanced setting (non default) have been set
    Goals:
        List all repository, and verify if GitHub advanced security is enabled
            For each repos:
            - Verify code scanning default setup
            - Verify branch protection settings
            - get the list of all used languages
    
    Output: a pandas dataframe containing the list of repos
    and the repo level info + code scanning info
'''

all_repos_columns =  [
        'Full Name',
        'Name',
        'Repo Languages',
        'Visibility',
        'Security And Analysis',
        'branches_url',
        'GHAS Default Config',
        'GHAS Language Config',
        'GHAS Schedule',
        'Url'
    ]


base_url = "https://api.GitHub.com"
access_token= "token "+ str(os.getenv("GITHUB_TOKEN"))
headers = {
    'Authorization': str(access_token)
}



def code_scanning_default_config(owner, repo):
    #doc: https://docs.github.com/en/rest/code-scanning/code-scanning?apiVersion=2022-11-28#get-a-code-scanning-default-setup-config
    #(change version to current one)
    code_scanning_default_url = base_url + "/repos/" + owner + "/" + repo + "/code-scanning/default-setup"
    try:
        response = requests.get(code_scanning_default_url, headers = headers).json()
        return response

    except requests.exceptions.RequestException as e: 
            print(" There was an issue loading"  + 
                    " the code scanning details")


def list(sdlc_repos_list = 'file.csv'):
    startTime = time.time()

    access_token = os.getenv("GITHUB_TOKEN")
    git = Github(access_token)
    all_repos = pd.DataFrame(columns=all_repos_columns)

    sdlc_repos = pd.read_csv(sdlc_repos_list, sep=";")
    for index, row in sdlc_repos.iterrows():
        try:
            repo = git.get_repo(row["full_name"])

            data = {
                        'Full Name' : repo.full_name,
                        'Url' : repo.html_url,
                        'Name' : repo.name,
                        'Repo Languages' : [repo.get_languages()],
                        'Visibility' : repo.visibility,
                        'Security And Analysis' : [repo.raw_data['security_and_analysis']],
                        'branches_url' : repo.branches_url,
                        'GHAS Default Config' : '',
                        'GHAS Language Config' : '',
                        'GHAS Schedule' : '',
            }
            # public repos have GHAS enabled by default (if enabled at the org level)
            # public repos will not have an advanced_security key.
            if repo.visibility  == "public" or repo.raw_data["security_and_analysis"]["advanced_security"]["status"] != "disabled":
                code_scan_config = code_scanning_default_config(repo.owner.login, repo.name)
                data['GHAS Default Config'] = code_scan_config["state"]
                data['GHAS Language Config'] = [code_scan_config["languages"]]
                data['GHAS Schedule'] = code_scan_config["schedule"]
            all_repos = pd.concat(
                [
                    all_repos,
                    pd.DataFrame(data,columns=all_repos.columns)
                ],
                axis = 0,
                ignore_index = True
            )
        except Exception as e:
             print("We can not pull info from the repo: "+ str(row["full_name"]))
             print(e)
             
    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
    #all_repos.to_csv('github/api/output/info_about_repos.csv', sep=',', encoding='utf-8',index=False)
    return all_repos

load_dotenv()
