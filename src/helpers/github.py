import requests
import sys
import json

import spacy
import xmltodict
import yake
from decouple import config
import base64

from lxml import etree

from contexts import is_code_context, docstring_context
from helpers.gpt import AllGPT
from helpers.transforms import get_is_code, get_language, clean_code, get_param_list
from storage.redis_store import RedisStore


class Github:
    def __init__(self, token=""):
        self.redis = RedisStore()
        self.token = token
        self.base_url = "https://api.github.com"
        self.all_gpt = AllGPT("gpt-3.5-turbo-1106")
        self.kw_extractor = yake.KeywordExtractor()
        self.nlp = spacy.load("en_core_web_sm")

    def get_project(self, path):
        path = path.replace("https://github.com/", "")
        # path = path.replace(self.base_url, "")
        path = path.split("/")
        return f"{path[0]}/{path[1]}"

    def get_repo_content(self, rel_path, path=""):
        # extract owner, repo, path from given path
        # print("ceva", rel_path, path)
        url = f"{self.base_url}/repos/{rel_path}/contents/{path}"

        value = self.redis.get(url)
        if value:
            print("FETCH ALREADY DONE")
            return value, url

        # print("dkfjvfdkjn", url)
        headers = {'Authorization': f'token {self.token}'} if self else {}
        response = requests.get(url, headers=headers)

        response.raise_for_status()
        try:
            response = response.json()
        except Exception as e:
            print("Error on conversion to json of the response")
            return None, None

        # add caching support
        self.redis.set(url, response, ttl=1000 * 30 * 30)
        print(response, url)
        return response, url

    def get_b64_content(self, path):
        headers = {'Authorization': f'token {self.token}'} if self else {}
        response = requests.get(path, headers=headers)
        response.raise_for_status()
        return response.json()

    def fetch_files(self, root_path, file=""):
        all_files = {}

        files, key = self.get_repo_content(root_path, file)
        for elem in files:
            content_path = f"{self.base_url}/repos/{root_path}/contents/{elem['path']}"
            # print(elem)
            if elem["type"] == "file":
                # verify if file is a text file
                response = requests.get(elem["download_url"])
                # print(f"A response with content type of {response.headers['content-type']}")
                if response and response.headers["content-type"].find("text") == 0:
                    # pair = (content_path, response.text)
                    all_files[elem['name']] = {"content": response.text, "key": content_path}
                    # all_files[elem['name']] = {"content": "", "key": content_path}

                    documentation = self.generate_documentation(all_files[elem['name']])
                    all_files[elem['name']].update(documentation)


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
            else:
                print(f"It s of type {elem['type']}, not accounted for")
        return all_files

    def generate_documentation(self, file_dict):
        content = file_dict.get("content")
        key_id = file_dict.get("key")
        code_context = is_code_context()
        code_context.append({
            "role": "user",
            "content": f"This is the text: {content}",
        })

        properties_key = f"{key_id}:properties"
        properties = RedisStore.get(properties_key)

        try:
            if len(content) > 100_000:
                raise AttributeError("Too long context")

            # calc props if not found
            if not properties:
                # print(len(all_gpt.tokenizer.encode(tree[key])))
                print("This is the code context", code_context)
                conditions = self.all_gpt.respond(code_context, max_tokens=1000)[0].get("content")
                properties = {
                    "code": get_is_code(conditions),
                    "language": get_language(conditions),
                }

                RedisStore.set(properties_key, properties, ttl=1000 * 30 * 30)
        except AttributeError as e:
            print("Context too large, we should skip")
            properties = {
                "code": False,
                "language": None
            }
            RedisStore.set(properties_key, properties, ttl=100 * 30 * 30)

        # in any of the cases, tag the file if it's a text file
        properties.update({"tags": self.tag_content(content)})

        if properties.get("code") and properties.get("language") == "PYTHON":
            # we should extract the code doc string
            content = clean_code(content)
            docstr_context = docstring_context()
            docstr_context.append({
                "role": "user",
                "content": f"THIS IS THE CODE: {content}",
            })

            docstring = self.all_gpt.respond(docstr_context, max_tokens=1500)[0].get("content")
            # split docstring after every documentation of the elem
            docstring = docstring.split("<documentation>")
            parser = etree.XMLParser(recover=True)

            doc_list = []
            for idx, doc_elem in enumerate(docstring):
                if idx == 0:
                    continue

                doc = etree.fromstring("<documentation>" + doc_elem, parser=parser)
                doc = etree.tostring(doc)
                doc_list.append(xmltodict.parse(doc))

            # processing the doc list
            doc_list = [
                {
                    "name": elem.get("documentation", {}).get("name"),
                    "description": elem.get("documentation", {}).get("description"),
                    'parameters': get_param_list(elem.get("documentation", {}).get("parameters")),
                    'return': elem.get("documentation", {}).get("return")
                }
                for elem in doc_list]

            # read stored info
            print("These are the properties", properties)
            properties.update({
                "documentation": doc_list
            })
            RedisStore.set(properties_key, properties, ttl=1000 * 30 * 30)

        return properties

    def tag_content(self, content):
        extracted_expr = [(kw, w) for kw, w in self.kw_extractor.extract_keywords(content)]
        wbow = {}
        for kw, w in extracted_expr:
            doc = self.nlp(kw.lower())
            # remove the stop words from the given text for greater quality embeddings and faster outputs
            lemmas = [token.lemma_ for token in doc if not (
                        token.is_punct or token.is_stop or token.like_num or token.like_url or token.like_email or token.is_currency)]

            if len(lemmas) == 0:
                continue

            w_len = w / len(lemmas)

            for word in lemmas:
                if not wbow.get(word):
                    wbow[word] = (0, 0)
                wbow[word] = (wbow[word][0] + w_len, wbow[word][1] + 1)

            # print(f"Weight of phrase {w} with lemmas: {lemmas}")

        wbow = sorted([(k, w / c) for k, (w, c) in wbow.items()], key=lambda x: x[1], reverse=True)
        return [kw for kw, w in wbow]

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
    # for key in tree:
    #     print(key, tree[key])

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
