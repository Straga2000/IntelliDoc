import re
from uuid import uuid4

def clean_code(text_code):
    # remove doubles, remove multiple lines
    text_code = text_code.replace('"', "'")
    text_code = re.sub('\n+', '\n', text_code)
    # remove commented lines
    text_code = re.sub('\s+#.+\n', '\n', text_code)
    return text_code


def get_is_code(condition):
    return True if re.search(".*CODE:.*YES", condition) else False


def get_language(condition):
    # split to language
    condition = condition.split("LANGUAGE:")
    if len(condition) <= 1:
        return None

    condition = re.sub("\s+", "", condition[1])
    return condition if condition != "-" else None


def get_documentation(doc_string):
    # doc_string = re.sub("\s+", "", doc_string)
    print(doc_string)
    doc_string = [elem for elem in re.findall(re.compile("en>"), doc_string)]
    return doc_string
    # doc_string = doc_string.split("</documentation>")

def get_random_id():
    return str(uuid4())


def get_param_list(param_data):
    if not param_data:
        return []
    if isinstance(param_data, dict):
        return [param_data]
    if isinstance(param_data, list):
        return param_data

if __name__ == "__main__":
    with open("../samples/doc_sample.txt") as f:
        doc_string = f.read()
        doc_string = clean_code(doc_string)
        print(get_documentation(doc_string))
