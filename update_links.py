import re


def update(new_link: str):
    with open('./data/links', 'r') as links_file_r:
        links = links_file_r.readlines()
        if re.match(r"^https://t.me/\w+/$", new_link):
            links.append(new_link)
        links = list(set(links))
        print(len(links))
    with open('./data/links', 'w') as links_file_w:
        upd_links = ''.join(links)
        links_file_w.write(upd_links)
