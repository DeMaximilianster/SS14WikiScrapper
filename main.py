from urllib.request import urlopen, Request
from urllib.parse import quote
import re
from typing import List


def scrape_from_site(url: str) -> str:
    request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    page = urlopen(request_site)
    html_bytes = page.read()
    return html_bytes.decode("utf-8")


def parse_history_for_oldids(html: str) -> List[int]:
    oldids = [int(x[-4:]) for x in re.findall("oldid=....", html)]
    oldids = sorted(set(oldids), reverse=True)
    return oldids


def search_in_old_versions(title: str, search_string: str, oldids: List[int]) -> str:
    first_present = None
    last_absent = None
    for index in range(len(oldids)):
        url = f"https://station14.ru/index.php?title={title}&oldid={oldids[index]}"
        html = scrape_from_site(url)
        if search_string.lower() in html.lower():
            first_present = oldids[index]
        elif first_present is not None:
            last_absent = oldids[index]
            break

    if first_present is None:
        return "Данных строк нет ни в одной версии статьи"
    elif last_absent is None:
        return "Данная строка была в статье с первой её версии:\n"\
               f"https://station14.ru/index.php?title={title}&oldid={first_present}"
    else:
        return "Вот обновление статьи, в которой появились данные строки\n" \
               f"https://station14.ru/index.php?title={title}&type=revision&diff={first_present}&oldid={last_absent}"


def find_first_appearance(title: str, search_string: str) -> str:
    title = quote(title.encode("cp1251"))
    url = f"https://station14.ru/index.php?title={title}&offset=&limit=500&action=history"
    html = scrape_from_site(url)
    oldids = parse_history_for_oldids(html)
    return search_in_old_versions(title, search_string, oldids)
