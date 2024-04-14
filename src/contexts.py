new_text = None
with open("samples/function_test.txt") as f:
    new_text = f.read().replace('"', "'")
    # print(new_text)

function_sample = None
with open("samples/function_example.txt") as f:
    function_sample = f.read().replace('"', "'")

function_docs = None
with open("samples/function_docs.txt") as f:
    function_docs = f.read().replace('"', "'")

non_function_sample = None
with open("samples/non_function_ex.txt") as f:
    non_function_sample = f.read().replace('"', "'")


def is_code_context():
    return [
            {
                "role": "system",
                "content": "You are a code recognizer expert. You know using expert knowledge if a text is a piece of code or not. If you think something is code, specify in what programming language.",
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
        ]


def docstring_context():
    return [
        {
            "role": "system",
            "content": "You are an expert python software developer that needs to write the documentation for "
                       "the python code."
                       " Write a xml list for every class and function containing the description, name of the "
                       "class/function, parameters and the type of the returned value."
                       "If requests "
                       "are used, specify the usage of forms or json. Use the notation given in the example below.",
        },
        {
            "role": "system",
            "name": "example_user",
            "content": f"THIS IS THE CODE: {function_sample}"
        },
        {
            "role": "system",
            "name": "example_assistant",
            "content": f"{function_docs}",
        },
]