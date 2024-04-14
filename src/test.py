import json
import re

from helpers.gpt import AllGPT
from helpers.gpt_defaults import GPTDefaults
from helpers.transforms import clean_code, get_is_code, get_language, get_param_list
from decouple import config
from helpers.github import Github
from storage.redis_store import RedisStore
from contexts import is_code_context, docstring_context
from lxml import etree
import xmltodict
from core.compiler import Compiler


# all_gpt = AllGPT("gpt-3.5-turbo-1106")
github_api = Github(config('GITHUB_TOKEN', default='no_key'))


if __name__ == "__main__":
    project_url = "https://github.com/pri1311/crunch/tree/master"
    project_url = github_api.get_project(project_url)
    new_tree = github_api.fetch_files(project_url, file="")
    print(new_tree)
    # compiled_tree = Compiler.compile_tree("https://github.com/pri1311/crunch/tree/master")
    # print(compiled_tree)
    # raise ValueError("fdvknfvkjgfdvou")
    # print(compiled_tree)
    # generated_tree = Compiler.generate_documentation(compiled_tree)
    # print(generated_tree)
