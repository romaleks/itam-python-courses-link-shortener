import re


def convert_link(link: str) -> str:
    if 'https://' not in link:
        link = 'https://' + link
    return link

def is_valid_link(link: str) -> bool:
    pattern = r'^(https?|ftp)://([^\s/$.?#]+\.)+[^\s/$.?#]+[^\s]*$'
    return bool(re.match(pattern, link))