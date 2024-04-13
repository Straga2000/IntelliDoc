import requests
import sys
import json
from decouple import config
import base64


class Github:
    def __init__(self, token=""):
        self.token = token
        self.base_url = "https://api.github.com"

    def get_project(self, path):
        path = path.replace("https://github.com/", "")
        # path = path.replace(self.base_url, "")
        path = path.split("/")
        return f"{path[0]}/{path[1]}"

    def get_repo_content(self, rel_path, path=""):
        # extract owner, repo, path from given path
        print("ceva", rel_path, path)
        url = f"{self.base_url}/repos/{rel_path}/contents/{path}"
        print("dkfjvfdkjn", url)
        headers = {'Authorization': f'token {self.token}'} if self else {}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_b64_content(self, path):
        headers = {'Authorization': f'token {self.token}'} if self else {}
        response = requests.get(path, headers=headers)
        response.raise_for_status()
        return response.json()

    def fetch_files(self, root_path, file=""):
        all_files = {}
        for elem in github_api.get_repo_content(root_path, file):
            content_path = f"{self.base_url}/repos/{root_path}/contents/{elem['path']}"
            # print(elem)
            if elem["type"] == "file":
                # verify if file is a text file
                response = requests.get(elem["download_url"])
                # print(f"A response with content type of {response.headers['content-type']}")
                if response and response.headers["content-type"].find("text") == 0:
                    # pair = (content_path, response.text)
                    all_files[elem['name']] = response.text
                    # all_files.append(pair)
                    # print(pair)
                    # content = self.get_b64_content(content_path).get("content")
                    # if content:
                    #     print(base64.b64decode(content))

                # with requests.get(elem["download_url"]) as r:
                # print(r.text)
            elif elem["type"] == "dir":
                returned_files = self.fetch_files(root_path, elem['path'])
                all_files[elem['path']] = returned_files
                # all_files.extend(returned_files)
        return all_files


    # def fetch_files(self, rel_path, path):
    #     # rel_path = self.get_project(path)
    #     print("aaaaaaaaaaaaaaa", rel_path, path)
    #     contents = self.get_repo_content(rel_path, path)
    #     for content in contents:
    #         print("this is the content", content)
    #         if content['type'] == 'file':
    #             print("ceva si aici", f"{rel_path}/{content['path']}")
    #         elif content['type'] == 'dir':
    #             print("hahahahaha", content["path"])
    #             self.fetch_files(rel_path, content['path'])


if __name__ == "__main__":
    github_api = Github(config('GITHUB_TOKEN', default='no_key'))
    given_url = "https://github.com/pri1311/crunch/tree/master"
    given_url = github_api.get_project(given_url)

    tree = github_api.fetch_files(given_url, "")
    for key in tree:
        print(key, tree[key])

    # print()
    # init_url = f"https://github.com/{given_url}/blob/master"

            # decoded = base64.b64decode(elem['content'])
            # print(decoded)

    # print(github_api.fetch_files(init_url, ""))

    # try:
    #     base_url, repo_details = repo.split("github.com/", 1)
    #     owner, repo = repo_details.split("/", 1)
    #     if repo.endswith("/"):
    #         repo = repo[:-1]
    #     if "/" in repo:
    #         repo = repo.split("/", 1)[0]
    # except ValueError:
    #     print("Invalid URL.")
    #     sys.exit(1)
    #
    # try:
    #     list_files(api, owner, repo, token=token, base_url=f"https://github.com/{owner}/{repo}/blob/master")
    # except requests.HTTPError as e:
    #     print(f"Failed to access GitHub API: {e}")
    #     sys.exit(1)
