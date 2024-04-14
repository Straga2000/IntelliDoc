import re

import xmltodict
from lxml import etree

from helpers.gpt import AllGPT
from helpers.gpt_defaults import GPTDefaults
from helpers.transforms import clean_code, get_is_code, get_language, get_param_list
from decouple import config
from helpers.github import Github
from storage.redis_store import RedisStore
from contexts import is_code_context, docstring_context

all_gpt = AllGPT("gpt-3.5-turbo-1106")
github_api = Github(config('GITHUB_TOKEN', default='no_key'))


class Compiler:
    def __init__(self):
        pass

    @classmethod
    def compile_tree(cls, project_url):
        project_url = github_api.get_project(project_url)
        return github_api.fetch_files(project_url, "")

    @classmethod
    def generate_documentation(cls, compiled_tree):
        documentation_list = {}
        for key in compiled_tree:
            content = compiled_tree[key].get("content")
            key_id = compiled_tree[key].get("key")

            if isinstance(content, str):
                code_context = is_code_context()
                code_context.append({
                    "role": "user",
                    "content": f"This is the text: {content}",
                })

                properties_key = f"{key_id}:properties"
                properties = RedisStore.get(properties_key)

                # calc props if not found
                if not properties:
                    # print(len(all_gpt.tokenizer.encode(tree[key])))
                    conditions = all_gpt.respond(code_context, max_tokens=1000)[0].get("content")
                    properties = {
                        "code": get_is_code(conditions),
                        "language": get_language(conditions),
                    }

                    RedisStore.set(properties_key, properties)

                if key_id.find("website") != -1:
                    print("This key is problematic", key, key_id, properties)

                if properties.get("code") and properties.get("language") == "PYTHON":
                    # we should extract the code doc string
                    content = clean_code(content)
                    docstr_context = docstring_context()
                    docstr_context.append({
                        "role": "user",
                        "content": f"THIS IS THE CODE: {content}",
                    })

                    docstring = all_gpt.respond(docstr_context, max_tokens=1500)[0].get("content")
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
                    RedisStore.set(properties_key, properties)
                documentation_list[key_id] = properties
            elif isinstance(content, dict):
                documentation_list[key_id] = cls.generate_documentation(content)
            else:
                print("Not of type str sau dict", content, key_id, key)
        return documentation_list
