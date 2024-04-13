import requests
import sys
import json
def get_issue(owner, repo, token, issue_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {'Authorization': f'Bearer {token}',"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_dictionary(dict, updated_dict):
    updated_dict.update(dict)
    return updated_dict

def update_issue(owner, repo, token ,issue_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {'Authorization': f'Bearer {token}',"Accept": "application/vnd.github+json"}
    text = update_dictionary({"title":"test update","body":"suggestion"},get_issue("Straga2000", "Foodity","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", 1))
    response = requests.patch(url, json=text,headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    update_issue("Straga2000", "Foodity","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", 1)

if __name__ == "__main__":
    main()
