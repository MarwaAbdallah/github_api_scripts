import json
import pandas as pd
import services.repos_service as rs
from dotenv import load_dotenv

'''
    This script compares the list of languages of SDLC repos
    to the list of languages supported by CodeQL. List available at:
    https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql#about-codeql

    PLEASE Update the below codeql_languages dictionary when new languages are added

    Possible values for Max CodeQL Coverage:

    -1: The reposotiry does not specify any language (it may be empty)
     0 to 100: degre of maximum coverage feasible using CodeQL

    IMPORTANT: we round up the coverage value.
    So if one of the languages is covered, but repreents a tiny bit of the repo(< 1%),
    the coverage value will still show up as 0%
    Note: The list of languages in a repo is provided by github:
    https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-repository-languages
'''
codeql_languages = [
    "C",
    "C++",
    "C#",
    "Go",
    "Java",
    "Kotlin",
    "Javascript",
    "TypeScript",
    "Python",
    "Ruby",
    "Swift"
]

def main():
    # This below additional steps serves for readibility purposes: 
    # So that the above original list stays human readable
    codeql_languages_lowercase = list(map(lambda x: x.lower(), codeql_languages))
    repos =  rs.list('input.csv')
    repos = repos[['Full Name', 'Name', 'Repo Languages', 'GHAS Default Config',  'GHAS Language Config', 'GHAS Schedule']]
    df = pd.DataFrame()

    for index, row in repos.iterrows():
        lang = str(row['Repo Languages']).replace("\'", "\"").lower()
        lang_dict = json.loads(lang)
        nb_bytes = sum(lang_dict.values())
        lang_coverage = 0
        lang_missed = 0
        scanned_languages = list(map(lambda x: x.lower(), row['GHAS Language Config']))
        missing_languages = []
        if len(scanned_languages) == 0:
            scanned_languages = []
        if nb_bytes == 0: #repo is empty or no languages reported
            row['Max CodeQL Coverage'] = -1
            row['Missing CodeQL Coverage'] = -1
        else:
            for l in codeql_languages_lowercase:
                #the language is used in the repo and GHAS supported, but NOT configured
                if lang_dict.get(l) is not None:
                    if l not in scanned_languages:
                        missing_languages.append(l)
                        lang_missed = lang_missed + lang_dict[l]
                
                    lang_coverage = lang_coverage + lang_dict[l]

            # Max Coverage
            row['Max CodeQL Coverage'] = int(round(lang_coverage * 100 / nb_bytes))
            # How much of the repo we could cover, but we don't
            if lang_coverage != 0:
                row['Missing CodeQL Coverage'] = round(lang_missed * 100 / lang_coverage)
            else:
                row['Missing CodeQL Coverage'] = 0
            # Missing Languages supported by CodeQL but not configured
            row['Missing Languages'] = missing_languages

        df = pd.concat(
            [
                df,
                row.to_frame().T
            ],
            axis = 0,
            ignore_index = True
        )
    df.to_csv('output.csv', sep=',', encoding='utf-8',index=False)

load_dotenv()
main()