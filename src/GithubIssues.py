import requests
import sys
import json
def get_issue(owner, repo, token, issue_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {'Authorization': f'Bearer {token}',"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_dictionary(new_dict, old_dict):
    # updated_dict.update(dict)
    # return updated_dict
    result_dict = {}
    for key in old_dict.keys():
            if key in new_dict and isinstance(new_dict[key],str) and isinstance(old_dict[key],str):
             result_dict[key] = old_dict[key] + " " + new_dict[key]
            else:
                result_dict[key] = old_dict[key]
    old_dict.update(result_dict)
    return old_dict

def update_issue(owner, repo, token ,issue_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {'Authorization': f'Bearer {token}',"Accept": "application/vnd.github+json"}
    text = update_dictionary({"title":"test test test","body":"suggestion"},get_issue("Straga2000", "Foodity","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", 1))
    response = requests.patch(url, json=text,headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    update_issue("Straga2000", "Foodity","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", 1)

if __name__ == "__main__":
    main()
