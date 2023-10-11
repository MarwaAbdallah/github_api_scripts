import pandas as pd
import services.repos_service as rs
from dotenv import load_dotenv

'''
   gets the list of repos using the Repo Service
   exports advanced security settings for each repository:
   - is Advanced security enabled?
   - is Secret Scanning enabled?
   - is Secret Scanning Push Protection enabled?
   - are Dependabot Security Update enabled?
'''
def set_advanced_security_value(sec_key):
    return(
        sec_key['advanced_security']['status']
        if 'advanced_security' in sec_key
        else 'Public Repository'
    )

def main():
    repos =  rs.list('input.csv')
    repos = repos[['Url','Full Name', 'Security And Analysis']]
    df = pd.DataFrame()

    for index, row in repos.iterrows():
        data = {
            'Full Name' : row['Full Name'],
            'Url' : row['Url'],
            'Advanced Security' : set_advanced_security_value(row['Security And Analysis']),
            'Secret Scanning' : row['Security And Analysis']['secret_scanning']['status'],
            'Secret Scanning Push Protection' : row['Security And Analysis']['secret_scanning_push_protection']['status'],
            'Dependabot Updates' : row['Security And Analysis']['dependabot_security_updates']['status'],
        }

        df = pd.concat(
            [
                df,
                pd.DataFrame(data, index=[0])
            ],
            axis = 0,
            ignore_index = True
        )
    df.to_csv('output.csv', sep=',', encoding='utf-8',index=False)

load_dotenv()
main()
