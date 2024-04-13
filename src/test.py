from helpers.gpt import AllGPT
from helpers.gpt_defaults import GPTDefaults
from helpers.transforms import clean_code
from decouple import config
from helpers.github import Github

new_text = None
with open("./function_test.txt") as f:
    new_text = f.read().replace('"', "'")
    # print(new_text)

function_sample = None
with open("./function_example.txt") as f:
    function_sample = f.read().replace('"', "'")

function_docs = None
with open("function_docs.txt") as f:
    function_docs = f.read().replace('"', "'")

non_function_sample = None
with open("non_function_ex.txt") as f:
    non_function_sample = f.read().replace('"', "'")


example_messages = [
        # {
        #     "role": "system",
        #     "content": "You are a software developer that needs to write the documentation for a python code. "
        #                "Please write in a standardize way the comments for the given code. If requests "
        #                "are used, specify the usage of forms or json. Use the notation given in the next example (:param:, :rtype:, ).",
        # },
        # {
        #     "role": "system",
        #     "name": "example_user",
        #     "content": function_sample
        # },
        # {
        #     "role": "system",
        #     "name": "example_assistant",
        #     "content": function_docs,
        # },
        # {
        #     "role": "system",
        #     "name": "example_user",
        #     "content": "Let's circle back when we have more bandwidth to touch base on opportunities for increased leverage.",
        # },
        # {
        #     "role": "system",
        #     "name": "example_assistant",
        #     "content": "Let's talk later when we're less busy about how to do better.",
        # },
        # {
        #     "role": "user",
        #     "content": new_text,
        # },
    ]

all_gpt = AllGPT("gpt-3.5-turbo-1106")
# completion = example_messages
# print("START RESPONSE HERE")
# print(all_gpt.respond(completion, max_tokens=500)[0]['content'])
github_api = Github(config('GITHUB_TOKEN', default='no_key'))
given_url = "https://github.com/pri1311/crunch/tree/master"
given_url = github_api.get_project(given_url)
tree = github_api.fetch_files(given_url, "")



for key in tree:

    content = tree[key].get("content")
    key_id = tree[key].get("key")
    if isinstance(content, str):
        example_messages = [
            {
                "role": "system",
                "content": "You are a code recognizer expert. You know using expert knowledge if a text is a piece of "
                           "code or not. If you think something is code, specify in what programming language.",
            },

            # {
            #     "role": "system",
            #     "content": "You are a software developer and you need to create a complete documentation of the code "
            #                "given below. If the given text is not code, create a summary of the file. "
            #                "On code, document using the name of the function or class, the parameters, and the return value.",
            # },
            {
                "role": "system",
                "name": "example_user",
                "content": function_sample
            },
            {
                "role": "system",
                "name": "example_assistant",
                "content": "CODE: YES\nLANGUAGE: PYTHON\n",
            },
            {
                "role": "system",
                "name": "example_user",
                "content": f"This is the text: {function_sample}"
            },
            {
                "role": "system",
                "name": "example_assistant",
                "content": "CODE: YES\nLANGUAGE: PYTHON\n",
            },
            {
                "role": "system",
                "name": "example_user",
                "content": f"This is the text: {non_function_sample}"
            },
            {
                "role": "system",
                "name": "example_assistant",
                "content": "CODE: NO\nLANGUAGE: -\n",
            },

            # {
            #     "role": "system",
            #     "name": "example_user",
            #     "content": "Let's circle back when we have more bandwidth to touch base on opportunities for increased leverage.",
            # },
            # {
            #     "role": "system",
            #     "name": "example_assistant",
            #     "content": "Let's talk later when we're less busy about how to do better.",
            # },
            # {
            #     "role": "user",
            #     "content": new_text,
            # },
        ]
        print(key)
        new_conv = [elem for elem in example_messages]
        new_conv.append({
            "role": "user",
            "content": f"This is the text: {content}",
        })
        # print(len(all_gpt.tokenizer.encode(tree[key])))
        print(all_gpt.respond(new_conv, max_tokens=1000))

        # print("Value for embedding", all_gpt.evaluate(tree[key], 0))
    # print(key, tree[key])
