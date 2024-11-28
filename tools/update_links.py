def update(new_link: str):
    with open('./config/links', 'r') as links_file_r:
        links = links_file_r.readlines()
        links.append(new_link+'\n')
        links = list(set(links))
    with open('./config/links', 'w') as links_file_w:
        upd_links = ''.join(links)
        links_file_w.write(upd_links)
