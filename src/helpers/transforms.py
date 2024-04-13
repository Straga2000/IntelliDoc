import re


def clean_code(text_code):
    # remove doubles, remove multiple lines
    text_code = text_code.replace('"', "'")
    text_code = re.sub('\n+', '\n', text_code)
    # remove commented lines
    text_code = re.sub('\s+#.+\n', '\n', text_code)
    return text_code
