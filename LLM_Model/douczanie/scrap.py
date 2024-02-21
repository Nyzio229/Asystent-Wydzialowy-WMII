import re
import json

from pathlib import Path
from itertools import chain
from typing import Generator, Optional, Callable

from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qs

import bs4
import requests

def remove_query_param_like(url: str, query_param_filter: str) -> str:
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query, keep_blank_values=True)

    # stwórz kopię `query`, żeby nie było błędu "RuntimeError: dictionary changed size during iteration"
    for param in list(query):
        if query_param_filter in param:
            query.pop(param)

    parsed_url = parsed_url._replace(query=urlencode(query, True))
    url = urlunparse(parsed_url)

    return url

HTML_SPACE = "\xa0"
BASE_URL = "https://www.mat.umk.pl"

def get_text(tag: bs4.Tag, with_links=True) -> str:
    _inline_elements = {
        "a", "b", "i", "s",
        "u", "em", "ol", "td",
        "tt", "ul", "bdo", "del",
        "sub", "sup", "wbr", "cite",
        "font", "mark", "span", "label",
        "button", "strong"
    }

    _single_newline_blocks = {"li", "div","tr", "br"}
    assert _single_newline_blocks-_inline_elements == _single_newline_blocks, "Blocking elements cannot be inline"

    def _filter_child(child: bs4.Tag) -> bs4.Tag:
        name = child.name
        if name == "tr":
            if list(filter(lambda string: not string.isspace(), child.find_all(string=True))):
                next_sibling = child.find_next_sibling("tr")
                if next_sibling:
                    strings = next_sibling.find_all(string=True)
                    strings = list(filter(lambda s: not s.isspace(), strings))

                    if len(strings) == 1:
                        # zamień spację na końcu obecnego <td> na przecinek i spację
                        text = child.find_all(string=True)[-1]
                        text.string = f"{text.string.strip()}, "

                        # jeśli jest np. nr telefonu podany w nowym wierszu (<tr>), to normalnie by dodało "\n",
                        # więc "wyciągnij" <td> z tego <tr>, przez co "\n" nie będzie dodane przy jego odczytywaniu
                        next_sibling.unwrap()

            return child

        # czasem jest tak dziwnie zrobione (np. jeden raz w "dziekanat" -> "e-mail"),
        # że <table> jest w <td> - wtedy znajdź pierwszy (w domyśle: jedyny)
        # wewnętrzny <td> i używaj go zamiast tego
        if name == "td" and child.find("table", recursive=False):
            child = child.find("td")

        return child

    def _get_all_text(tag: bs4.Tag) -> str:
        return "".join(_get_text(tag))

    def _get_text(root: bs4.Tag) -> Generator:
        for child in root.children:
            if isinstance(child, bs4.Tag):
                child = _filter_child(child)

                def _has_class(classes: set[str]):
                    return set(child.get("class", [])) & classes

                # pomiń nagłówek/stopkę na stronie z seminariami
                if _has_class({"seminarportlet_main_menu", "seminarportlet_footer"}):
                    continue

                name = child.name

                def _is_all_spaces(tag: bs4.Tag):
                    return tag.name == "u" and not set(tag.string)-set((" ", HTML_SPACE))

                # zamień odstępy (które na stronie są spacjami) na gwiazdki
                if _is_all_spaces(child):
                    # dodaj nową linię przed odstępem i po nim (odstępy są z jakiegoś powodu podzielone na kilka tagów)
                    def _should_add_newline(which_sibling: str) -> bool:
                        sibling: Optional[bs4.Tag] = getattr(child, f"{which_sibling}_sibling")

                        return not sibling or not _is_all_spaces(sibling)

                    if _should_add_newline("previous"):
                        yield "\n"

                    yield "-" * len(child.string)

                    if _should_add_newline("next"):
                        yield "\n"

                    continue

                # <hr> = pozioma linia
                if name == "hr":
                    yield "-" * 50

                # sprawdź czy ten element jest elementem blokującym
                # (ale tylko jeśli ten element nie jest w <li>, bo wtedy
                # np. <li><p>test</p></li> dałoby nową linię po gwiazdce oznaczającej element listy)
                if child.parent.name != "li" and name not in _inline_elements:
                    newline_count = 1 if name in _single_newline_blocks else 2
                    yield "\n" * newline_count

                # pogrub tekst, który w html powinien być pogrubiony
                # + dodatkowo w seminariach temat seminarium i nazwa wykładowcy
                if name in {"strong", "b"} or _has_class({"topic", "lecturer_name"}):
                    bold_mark = "*"
                    bold_text = _get_all_text(child).replace(HTML_SPACE, " ")

                    if bold_text and not bold_text.isspace():
                        l_idx = len(bold_text)-len(bold_text.lstrip())
                        r_idx = len(bold_text.rstrip())

                        prefix = bold_text[:l_idx]
                        text = bold_text[l_idx:r_idx]
                        suffix = bold_text[r_idx:]

                        yield text.join([bold_mark]*2).join([prefix, suffix])

                        continue

                if name == "li":
                    def _find_li_parent(el: bs4.Tag) -> Optional[bs4.Tag]:
                        return el.find_parent("li")

                    li_parent = _find_li_parent(child)

                    if li_parent:
                        # jeśli to wewnętrzna lista, to dodaj tabulację od lewej
                        n_parents = 0

                        while li_parent:
                            li_parent = _find_li_parent(li_parent)
                            n_parents += 1

                        yield "\t" * n_parents

                    parent_name = child.parent.name

                    # "unordered list" - nie ma indeksu, tylko kropka przed elementem
                    if parent_name == "ul":
                        prefix = "*"
                    # "ordered list" - indeks liczbowy przed elementem
                    elif parent_name == "ol":
                        idx = len(child.find_previous_siblings("li"))
                        prefix = f"{idx+1}."
                    else:
                        raise ValueError(f"Unknown parent for 'li' tag: '{parent_name}'. Should be 'ul' or 'ol'")

                    yield f"{prefix} "

                    # jeśli to ostatni <li> to dodaj dodatkowy odstęp
                    is_last = not child.find_next_sibling("li")

                    if is_last:
                        yield _get_all_text(child).strip()
                        yield "\n\n"

                        continue

                # nagłówki html: od <h1> do <h6>
                header_tag_names = frozenset(f"h{i}" for i in range(1, 7))

                # jeśli to nagłówek (który nie ma klasy - wtedy wiemy, że to nie jest tytuł)
                # to dodaj gwiazdki żeby się wyróżniał
                if name in header_tag_names and not child.has_attr("class"):
                    header_text =  _get_all_text(child).strip()

                    # czasem nagłówe jest pusty, więc sprawdź to najpierw
                    if header_text:
                        bold_mark = "*** "
                        yield header_text.join((bold_mark, bold_mark[::-1]))

                    continue

                yield from _get_text(child)

                # czasem <a> nie ma atrybutu "href"
                if with_links and name == "a" and child.has_attr("href"):
                    url = child["href"]

                    # usuń "redirect" bo czasem jest obecny i sprawia, że url jest bardzo długi
                    url = remove_query_param_like(url, "redirect")
                    url = urljoin(BASE_URL, url)

                    # pomiń jeśli:
                    # 1. tekst linku jest pusty (np. jeśli jest to obrazek)
                    # 2. spacja jest w urlu (w jednym miejscu jest błąd: href="https://W dniach od 31 lipca do 6 się (...)")
                    # 3. jeśli link to wysyłanie maila
                    # 4. jeśli link już w tekście zawiera odnośnik
                    # (samo `child.string` nie zawsze działa, np. jeśli w tekście jest kolejny tag)
                    link_text = _get_all_text(child).strip()

                    if link_text and " " not in url and not url.startswith("mailto:") and url != link_text:
                        yield f" (link: {url})"
            # pomiń komentarze html (<!-- komentarz tutaj -->), skrypty, arkusze stylów i szablony
            elif isinstance(child, bs4.NavigableString) and not isinstance(child, (bs4.Comment, bs4.Script, bs4.Stylesheet, bs4.TemplateString)):
                yield child.string

    return _get_all_text(tag)

def get_filtered_text(tag: bs4.Tag, with_links=True) -> str:
    text = get_text(tag, with_links)

    # czasem jest niewidzialny znak ("Soft hyphen"), który sprawia, że
    # w słowach pojawiają się odstępy
    text = text.replace("\xad", "")
    text = text.replace(HTML_SPACE, " ")

    # zamień 2 lub więcej spacji na 1
    text = re.sub(" +", " ", text)
    # zamień spację + \n na \n
    text = re.sub(" \n", "\n", text)
    # zamień 3 lub więcej \n na \n\n
    text = re.sub("\n{3,}", "\n\n", text)
    # zamień \n + spacja na \n
    text = re.sub("\n ", "\n", text)
    #" (AT) " lub " [AT] " - napraw e-maile (re.IGNORECASE, bo czasem jest to "AT", czasem "at")
    # (uwzględnij gwiazdki, bo one oznaczają pogrubiony tekst, a tekst dookoła "AT" czasem jest pogrubiony)
    text = re.sub(r"[ \*]?[\(|\[]at[\)|\]][ \*]?", "@", text, flags=re.IGNORECASE)

    text = text.strip()

    return text

def soup_for(url: str) -> bs4.BeautifulSoup:
    # bez "User-Agent" jest błąd 404
    response = requests.get(url,
                            headers={
                                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                "Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582")
                            },
                            timeout=30)

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    return soup

def get_text_for_tag_of_class(tag: bs4.Tag, html_tag: str, html_class: str) -> str:
    tag = tag.find(html_tag, html_class)
    text = get_filtered_text(tag)
    return text

def get_data_from_portlets(soup: bs4.BeautifulSoup) -> list:
    def _get_portlet_data(portlet: bs4.Tag) -> Optional[dict[str, str | list]]:
        portlet_body = portlet.find("div", "portlet-body")

        news_elements = portlet_body.find_all("div", "news-element", recursive=False)

        news_body = []
        for news in news_elements:
            original_news = news
            title = news.find("div", "news-title", recursive=False)

            title_link = title.find("a", recursive=False)

            if title_link:
                new_soup = soup_for(title_link["href"])
                news = new_soup.find("div", "news-return").parent

            title = get_filtered_text(title, with_links=False)
            abstract = get_text_for_tag_of_class(news, "div", "news-abstract")

            # pomiń jeśli treść jest pusta
            if abstract:
                news_data = dict(title=title,
                                 date=get_text_for_tag_of_class(news, "div", "news-data"),
                                 abstract=abstract)
                news_body.append(news_data)

            original_news.decompose()

        articles_body = []
        content_articles = portlet_body.find_all("div", "journal-content-article", recursive=False)
        for article in content_articles:
            article_data = get_filtered_text(article)

            # pomiń jeśli treść jest pusta
            if article_data:
                articles_body.append(article_data)

            article.decompose()

        # czasem jest tekst bezpośrednio pod "portlet-body" - bez żadnej pośredniej klasy jak np. "journal-content-article"
        stray_text = get_filtered_text(portlet_body)

        # pomiń jeśli nie ma żadnej treści
        if not news_body and not articles_body and not stray_text:
            return None

        portlet_title = get_text_for_tag_of_class(portlet, "span", "portlet-title-text")

        articles_data = dict(section_title=portlet_title,
                             news=news_body,
                             articles=articles_body,
                             stray_text=stray_text)

        return articles_data

    # wpisy m.in. ze strony głównej
    portlets = soup.select(".portlet")

    portlets_data = list(filter(None, map(_get_portlet_data, portlets)))

    return portlets_data

def get_data_from_portlets_article(soup: bs4.BeautifulSoup):
    def _get_article_data(portlet: bs4.Tag, article_class: str) -> Optional[dict[str, str]]:
        article = portlet.find("div", article_class)

        if article is None:
            return None

        title = article.find("h1")
        if title:
            title_text = get_filtered_text(title)
            # usuń tytuł żeby pobrać tekst wpisu, który jest całą resztą
            title.decompose()
        # title może być pusty, jeśli np. artykuł jest podzielony na dwie części i jest odstęp między tymi częściami
        else:
            title_text = ""

        article = get_filtered_text(article)

        # pomiń jeśli treść jest pusta
        if not article:
            return None

        article_data = dict(
            title=title_text,
            body=article
        )

        return article_data

    # wpisy z innych stron (np. "konkursy i koła") oraz poboczne wpisy (np. "Archiwum")
    portlets = soup.select(".portlet-borderless-container")

    data = (list(map(lambda portlet: _get_article_data(portlet, f"article{suffix}"), portlets))
            for suffix in ("p", "b", "c"))
    data = list(filter(None, chain(*data)))

    return data

def get_page_content(soup: bs4.BeautifulSoup) -> list[dict[str, str | list]]:
    first = get_data_from_portlets_article(soup)
    second = get_data_from_portlets(soup)

    return first + second

def save(path: str, urls: list) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(urls):
        name = urlparse(url).path.strip("/").replace("/", ".")
        file_path = path / f"{i+1}_{name}.json"

        print(">", f"[{i+1}/{len(urls)}]", file_path)

        data = dict(
            origin=url,
            page_content=get_page_content(soup_for(url))
        )

        with open(file_path, "w", encoding="utf8") as file:
            json.dump(data, file, ensure_ascii=False, indent=3)

def resolve_sub_pages(
    base_url: str,
    sub_page_entry: dict[str] | list[str],
    on_url_resolved: Callable[[str], None]
) -> None:
    def _join_sub_page(sub_page_name: str) -> str:
        return "/".join((base_url, sub_page_name))

    def _resolve_sub_page_entry_dict(sub_page_entry: dict[str], on_url_resolved: Callable[[str], None]) -> None:
        for sub_page_name, child_sub_page_entry in sub_page_entry.items():
            resolve_sub_pages(_join_sub_page(sub_page_name), child_sub_page_entry, on_url_resolved)

    if isinstance(sub_page_entry, list):
        for sub_page_name in sub_page_entry:
            if isinstance(sub_page_name, str):
                on_url_resolved(_join_sub_page(sub_page_name))
            elif isinstance(sub_page_name, dict):
                _resolve_sub_page_entry_dict(sub_page_name, on_url_resolved)
    elif isinstance(sub_page_entry, dict):
        _resolve_sub_page_entry_dict(sub_page_entry, on_url_resolved)

def resolve_urls(sub_pages: dict[str, list]) -> list[str]:
    urls = []

    resolve_sub_pages(BASE_URL, sub_pages, urls.append)

    return urls

def main():
    sub_pages = {
        "web": [
            "samorzad",
            "komisja-stypendialna",
            "kni",
            "knm",
            {
                "struktura": [
                    "laboratorium-eksploatacji-systemu-komputerowego"
                ],
                "wmii": [
                    "glowna",
                    "dziekanat",
                    "rekrutacja",
                    "konkursy-i-kola",
                    "otwarta-pracownia-komputerowa",
                    "rada-dziekanska",
                    "wydzial",
                    "polskie-konsorcjum-narodowe",
                    "spis-instytucji-czlonkowskich",
                    "interesariusze-zewnetrzni",
                    "rada-dyscypliny-matematyka",
                    "rada-rozwoju-dyscypliny-informatyka",
                    "najlepsi-studenci-i-absolwenci-wydzialu-matematyki-i-informatyki-umk",
                    "muzeum-informatyki",
                    "granty",
                    "lista-doktoratow",
                    "habilitacje",
                    "seminaria",
                    {
                        "wydzial": [
                            "wladze",
                            "administracja",
                            "nauczyciele-akademiccy",
                            "misja",
                            "badania"
                        ],
                        "studia": {
                            "studia-doktoranckie": [
                                "matematyka"
                            ]
                        },
                        "sprawy-studenckie": [
                            "praktyki-zawodowe",
                            "praktyki-przedmiotowo-metodyczne",
                            "praktyki-psychologiczno-pedagogiczne",
                            "program-erasmus",
                            "program-azure-dev-tools-for-teaching"
                        ],
                        "rekrutacja": [
                            "matematyka-i-ekonomia",
                            "matematyka",
                            "matematyka-stosowana",
                            "informatyka",
                            "informatyka-studia-inzynierskie",
                            "analiza-danych",
                            "studia-niestacjonarne"
                        ]
                    },
                    "aktualnosci-dziekanatu",
                    "fundusze-europejskie-klucz",
                    "fundusze-europejskie-udzial-studentow-wmii-umk-w-miedzynarodowych-konkursach-matematycznych",
                    "fundusze-europejskie-rozwoj-wybitnych-studentow-informatyki-wmii-umk"
                ],
                "kni": [
                    "czlonkowie",
                    "kontakt"
                ],
                "knm": [
                    "dydaktyka",
                    "konsultacje-naukowe",
                    "dzialalnosc-naukowa",
                    "o-nas",
                    "czlonkowie",
                    "newsletter-informatyczny",
                    "kontakt"
                ]
            }
        ]
    }

    urls = resolve_urls(sub_pages)

    n = 25
    save("dump", urls[:n])

if __name__ == "__main__":
    main()
