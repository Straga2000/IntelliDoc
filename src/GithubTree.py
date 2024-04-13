import requests
import sys
import json
def get_repo_content(api, owner, repo, path="", token=None):
    url = f"{api}/{owner}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {token}'} if token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def list_files(api, owner, repo, path="", token=None,  base_url=""):
    contents = get_repo_content(api, owner, repo, path, token)
    for content in contents:
        if content['type'] == 'file':
            print(f"{base_url}/{content['path']}")
        elif content['type'] == 'dir':
            list_files(api, owner, repo, content['path'], token, base_url)

def main():
    with open("Administrative.json") as f:
        dictionary = json.load(f)
        token = dictionary["token"]
        repo = dictionary["repo_url"]
        api = dictionary["github_api"]
    try:
        base_url, repo_details = repo.split("github.com/", 1)
        owner, repo = repo_details.split("/", 1)
        if repo.endswith("/"):
            repo = repo[:-1]
        if "/" in repo:
            repo = repo.split("/", 1)[0]
    except ValueError:
        print("Invalid URL.")
        sys.exit(1)

    try:
        list_files(api, owner, repo, token=token, base_url=f"https://github.com/{owner}/{repo}/blob/master")
    except requests.HTTPError as e:
        print(f"Failed to access GitHub API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
