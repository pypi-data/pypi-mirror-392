import re


def normalize_text(text):
    result = re.sub(r'[^a-z0-9 -]', ' ', text,
                    flags=re.IGNORECASE | re.MULTILINE)
    result = re.sub(r'( +)', ' ', result, flags=re.IGNORECASE | re.MULTILINE)

    return result.strip()
