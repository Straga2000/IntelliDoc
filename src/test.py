from helpers.gpt import AllGPT
from helpers.gpt_defaults import GPTDefaults
from helpers.transforms import clean_code

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

print("Initial")
print({"init": clean_code(new_text)})


example_messages = [
        {
            "role": "system",
            "content": "You are a software developer that needs to write the documentation for a python code. "
                       "Please write in a standardize way the comments for the given code. If requests "
                       "are used, specify the usage of forms or json. Use the notation given in the next example (:param:, :rtype:, ).",
        },
        {
            "role": "system",
            "name": "example_user",
            "content": function_sample
        },
        {
            "role": "system",
            "name": "example_assistant",
            "content": function_docs,
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
        {
            "role": "user",
            "content": new_text,
        },
    ]

all_gpt = AllGPT("gpt-3.5-turbo-1106")
completion = example_messages
print("START RESPONSE HERE")
print(all_gpt.respond(completion, max_tokens=500)[0]['content'])
