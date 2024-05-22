import re

from pathlib import Path
from itertools import chain
from typing import Generator, Optional, Callable

from urllib.parse import (
    urljoin,
    urlencode,
    urlparse,
    urlunparse,
    parse_qs
)

import bs4
import requests

from utils import (
    get_docs_root_dir_path,
    save_json
)

def remove_query_param_like(
    url: str,
    query_param_filter: str
) -> str:
    parsed_url = urlparse(url)

    query = parse_qs(
        parsed_url.query, keep_blank_values=True
    )

    # stwórz kopię `query`, żeby nie było błędu
    # "RuntimeError: dictionary changed size during iteration"
    for param in list(query):
        if query_param_filter in param:
            query.pop(param)

    parsed_url = parsed_url._replace(
        query=urlencode(query, True)
    )

    url = urlunparse(parsed_url)

    return url

HTML_SPACE = "\xa0"
BASE_URL = "https://www.mat.umk.pl"

def get_text(tag: bs4.Tag, with_links=True) -> str:
    _inline_elements = {
        "a", "b", "i", "s", "u",
        "em", "ol", "td", "tt", "ul", "th",
        "bdo", "del", "img", "sub", "sup", "wbr",
        "cite", "font", "mark", "span",
        "button", "label", "strong"
    }

    _single_newline_blocks = {
        "p", "li", "div","tr", "br"
    }

    assert _single_newline_blocks.isdisjoint(
        _inline_elements
    ), "Blocking elements cannot be inline"

    def _is_all_spaces(text: str) -> bool:
        return not text or text.isspace()

    def _filter_child(child: bs4.Tag) -> bs4.Tag:
        name = child.name

        def _find_non_space_strings(tag: bs4.Tag) -> list[str]:
            return list(filter(
                lambda string: not _is_all_spaces(string),
                tag.find_all(string=True)
            ))

        if name == "tr":
            if _find_non_space_strings(child):
                next_sibling = child.find_next_sibling("tr")

                if next_sibling:
                    strings = _find_non_space_strings(
                        next_sibling
                    )

                    if len(strings) == 1:
                        # zamień spację na końcu obecnego <td> na przecinek i spację
                        text = child.find_all(string=True)[-1]
                        text.string = f"{text.string.strip()}, "

                        # jeśli jest np. nr telefonu podany w nowym wierszu (<tr>),
                        # to normalnie by dodało "\n", więc "wyciągnij" <td> z tego <tr>,
                        # przez co "\n" nie będzie dodane przy jego odczytywaniu
                        next_sibling.unwrap()

            return child

        # czasem jest tak dziwnie zrobione
        # (np. jeden raz w "dziekanat" -> "e-mail"),
        # że <table> jest w <td> - wtedy znajdź pierwszy
        # (w domyśle: jedyny) wewnętrzny <td> i używaj go zamiast tego
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
                    return set(
                        child.get("class", [])
                    ) & classes

                # pomiń nagłówek/stopkę na stronie z seminariami
                if _has_class({
                    "seminarportlet_main_menu", "seminarportlet_footer"
                }):
                    continue

                name = child.name

                def _is_u_tag_all_spaces(tag: bs4.Tag) -> bool:
                    return (
                        tag.name == "u" and
                        _is_all_spaces(tag.string)
                    )

                # zamień odstępy (które na stronie są spacjami) na gwiazdki
                if _is_u_tag_all_spaces(child):
                    # dodaj nową linię przed odstępem i po nim
                    # (odstępy są z jakiegoś powodu podzielone na kilka tagów)
                    def _should_add_newline_for_sibling(
                        which_sibling: str
                    ) -> bool:
                        sibling: Optional[bs4.Tag] = getattr(
                            child, f"{which_sibling}_sibling"
                        )

                        return (
                            not sibling or
                            not _is_u_tag_all_spaces(sibling)
                        )

                    if _should_add_newline_for_sibling("previous"):
                        yield "\n"

                    yield "-" * len(child.string)

                    if _should_add_newline_for_sibling("next"):
                        yield "\n"

                    continue

                # <hr> = pozioma linia
                if name == "hr":
                    yield "-" * 50

                def _should_add_newline(tag: bs4.Tag) -> bool:
                    parent = tag.parent

                    parent_name = parent.name

                    # np. <li><p>test</p></li> dałoby nową linię
                    # po gwiazdce oznaczającej element listy)
                    if parent_name == "li":
                        return False

                    name = tag.name

                    if name in _inline_elements:
                        return False

                    def _get_children(
                        tag: bs4.Tag
                    ) -> list[bs4.PageElement]:
                        return list(filter(
                            lambda child: (
                                # z jakiegoś powodu nawet jeśli jest np.
                                # `<td><p>Text</p></td>`,
                                # to i tak w `<p>.parent.children`
                                # są dodatkowo spacje: " " i " "
                                not child.isspace()
                                if isinstance(child, str)
                                else True
                            ),
                            tag.children
                        ))

                    # `<p><strong>Nagłówek</strong></p>`
                    # itp. jest tylko wtedy, kiedy
                    # element zewnętrzny (tutaj: <p>) jest jedynym dzieckiem
                    if len(_get_children(parent)) > 1:
                        return True

                    children = _get_children(tag)

                    n_children = len(children)

                    if n_children != 1:
                        return True

                    child = children[0]

                    # czasem jest np.
                    # <td><p><strong>Nagłówek</strong></p></td>
                    # i przed tym nagłówkiem nie powinno być nowej linii
                    # (czasem jest też samo
                    # <td><p>Nagłówek</p></td> - bez <strong></strong>)
                    def _is_only_child_tag_strong() -> bool:
                        return (
                            isinstance(child, bs4.Tag) and
                            child.name == "strong"
                        )

                    if parent_name != "td":
                        return True

                    # czasem jest pojedynczy <div> wewnątrz <td>
                    # i tam nie powinno być nowej linii
                    if name == "div":
                        return False

                    def _is_only_child_string() -> bool:
                        return isinstance(child, str)

                    if name != "p":
                        return True

                    return (
                        not _is_only_child_string() and
                        not _is_only_child_tag_strong()
                    )

                if _should_add_newline(child):
                    newlines_count = (
                        1
                        if name in _single_newline_blocks
                        else 2
                    )

                    yield "\n" * newlines_count

                # pogrub tekst, który w html powinien być pogrubiony
                # + dodatkowo w seminariach temat seminarium i nazwa wykładowcy
                if name in {
                    "strong", "b"
                } or _has_class({
                    "topic", "lecturer_name"
                }):
                    bold_mark = "*"
                    bold_text = _get_all_text(child).replace(
                        HTML_SPACE, " "
                    )

                    if not bold_text.isspace():
                        l_idx = len(bold_text)-len(bold_text.lstrip())
                        r_idx = len(bold_text.rstrip())

                        prefix = bold_text[:l_idx]
                        text = bold_text[l_idx:r_idx]
                        suffix = bold_text[r_idx:]

                        yield text.join(
                            [bold_mark]*2
                        ).join(
                            [prefix, suffix]
                        )

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
                        raise ValueError(
                            f"Unexpected parent for 'li' tag: '{parent_name}'. "
                            "Should be 'ul' or 'ol'"
                        )

                    yield f"{prefix} "

                    # jeśli to ostatni <li> to dodaj dodatkowy odstęp
                    is_last = not child.find_next_sibling("li")

                    if is_last:
                        yield _get_all_text(child).strip()
                        yield "\n\n"

                        continue

                if name == "td":
                    # czasem
                    # (np. "https://www.mat.umk.pl/web/wmii/wydzial/nauczyciele-akademiccy")
                    # połączenie <td> sprawia że nie ma odstępów pomiędzy kolejnymi komórkami
                    # w tabeli, więc je dodaj
                    text = _get_all_text(child)

                    if not _is_all_spaces(text):
                        yield f" {text} "

                    continue

                # nagłówki html: od <h1> do <h6>
                header_tag_names = frozenset(
                    f"h{i}" for i in range(1, 7)
                )

                # jeśli to nagłówek (który nie ma klasy -
                # wtedy wiemy, że to nie jest tytuł)
                # to dodaj gwiazdki żeby się wyróżniał
                if (
                    name in header_tag_names and
                    not child.has_attr("class")
                ):
                    header_text =  _get_all_text(child).strip()

                    # czasem nagłówe jest pusty, więc sprawdź to najpierw
                    if header_text:
                        bold_mark = "*** "
                        yield header_text.join((
                            bold_mark, bold_mark[::-1]
                        ))

                    continue

                yield from _get_text(child)

                # czasem <a> nie ma atrybutu "href"
                if with_links and name == "a" and child.has_attr("href"):
                    url = child["href"]

                    # usuń "redirect" bo czasem jest obecny i
                    # sprawia, że url jest bardzo długi
                    url = remove_query_param_like(url, "redirect")
                    url = urljoin(BASE_URL, url)

                    # pomiń jeśli:
                    # 1. jeśli link jest zbyt długi
                    # 2. spacja jest w urlu (w jednym miejscu jest błąd:
                    #    href="https://W dniach od 31 lipca do 6 się (...)")
                    # 3. jeśli link to wysyłanie maila
                    # 4. jeśli link już w tekście zawiera odnośnik
                    # (samo `child.string` nie zawsze działa,
                    # np. jeśli w tekście jest kolejny tag)
                    link_text = _get_all_text(child).strip()

                    MAX_URL_LENGTH = 70

                    if (
                        len(url) <= MAX_URL_LENGTH and
                        " " not in url and
                        not url.startswith("mailto:") and
                        url != link_text
                    ):
                        yield f" (link: {url})"
            # pomiń komentarze html (<!-- komentarz tutaj -->),
            # skrypty, arkusze stylów i szablony
            elif (
                isinstance(child, bs4.NavigableString) and
                not isinstance(child, (
                    bs4.Comment, bs4.Script,
                    bs4.Stylesheet, bs4.TemplateString
                ))
            ):
                yield child.string

    return _get_all_text(tag)

def get_filtered_text(
    tag: bs4.Tag,
    with_links: bool = True
) -> str:
    text = get_text(tag, with_links)

    # czasem jest niewidzialny znak ("Soft hyphen"),
    # który sprawia, że w słowach pojawiają się odstępy
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

    #" (AT) " lub " [AT] " - napraw e-maile
    # (re.IGNORECASE, bo czasem jest to "AT", czasem "at")
    # (uwzględnij gwiazdki, bo one oznaczają pogrubiony tekst,
    # a tekst dookoła "AT" czasem jest pogrubiony)
    text = re.sub(
        r"[ \*]?[\(|\[]at[\)|\]][ \*]?",
        "@", text, flags=re.IGNORECASE
    )

    # (czasem jest błąd, że nie ma '[]' ani
    # '()' wokół 'AT', więc trzeba to uwzględnić)
    text = re.sub(
        r"atmat\.umk\.pl", "@mat.umk.pl",
        text, flags=re.IGNORECASE
    )

    # czasem znaki interpunkcyjne są ze spacją przed sobą - trzeba naprawić
    text = re.sub(" ,([^,])", r",\1", text)
    text = re.sub(r" ([\.!])", r"\1", text)

    text = text.strip()

    return text

def get_soup(url: str) -> bs4.BeautifulSoup:
    # bez "User-Agent" jest błąd 404
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    )

    response = requests.get(
        url,
        headers={
            "User-Agent": user_agent
        },
        timeout=30
    )

    response.raise_for_status()

    soup = bs4.BeautifulSoup(
        response.content, "html.parser"
    )

    return soup

def get_text_for_tag_of_class(
    tag: bs4.Tag,
    html_tag: str,
    html_class: str
) -> str:
    tag = tag.find(html_tag, html_class)
    text = get_filtered_text(tag)

    return text

def get_data_from_portlets(
    soup: bs4.BeautifulSoup
) -> list:
    def _get_portlet_data(
        portlet: bs4.Tag
    ) -> Optional[dict[str, str | list]]:
        portlet_body = portlet.find(
            "div", "portlet-body"
        )

        news_elements = portlet_body.find_all(
            "div", "news-element", recursive=False
        )

        news_body = []

        for news in news_elements:
            original_news = news
            title = news.find(
                "div", "news-title", recursive=False
            )

            title_link = title.find("a", recursive=False)

            if title_link:
                new_soup = get_soup(title_link["href"])
                news = new_soup.find("div", "news-return").parent

            title = get_filtered_text(title, with_links=False)

            abstract = get_text_for_tag_of_class(
                news, "div", "news-abstract"
            )

            # pomiń jeśli treść jest pusta
            if abstract:
                news_data = dict(
                    title=title,
                    date=get_text_for_tag_of_class(
                        news, "div", "news-data"
                    ),
                    abstract=abstract
                )
                news_body.append(news_data)

            original_news.decompose()

        articles_body = []

        content_articles = portlet_body.find_all(
            "div", "journal-content-article", recursive=False
        )

        for article in content_articles:
            article_data = get_filtered_text(article)

            # pomiń jeśli treść jest pusta
            if article_data:
                articles_body.append(article_data)

            article.decompose()

        # czasem jest tekst bezpośrednio pod "portlet-body" -
        # bez żadnej pośredniej klasy jak np. "journal-content-article"
        stray_text = get_filtered_text(portlet_body)

        # pomiń jeśli nie ma żadnej treści
        if (
            not news_body and
            not articles_body and
            not stray_text
        ):
            return None

        portlet_title = get_text_for_tag_of_class(
            portlet, "span", "portlet-title-text"
        )

        articles_data = dict(
            section_title=portlet_title,
            news=news_body,
            articles=articles_body,
            stray_text=stray_text
        )

        return articles_data

    # wpisy m.in. ze strony głównej
    portlets = soup.select(".portlet")

    portlets_data = list(filter(
        lambda x: x,
        map(
            _get_portlet_data,
            portlets
        )
    ))

    return portlets_data

def get_data_from_portlets_article(
    soup: bs4.BeautifulSoup
) -> list:
    def _get_article_data(
        portlet: bs4.Tag,
        article_class: str
    ) -> Optional[dict[str, str]]:
        article = portlet.find(
            "div", article_class
        )

        if article is None:
            return None

        title = article.find("h1")
        if title:
            title_text = get_filtered_text(title)
            # usuń tytuł żeby pobrać tekst wpisu, który jest całą resztą
            title.decompose()
        # title może być pusty, jeśli np. artykuł jest
        # podzielony na dwie części i jest odstęp między tymi częściami
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

    # wpisy z innych stron (np. "konkursy i koła")
    # oraz poboczne wpisy (np. "Archiwum")
    portlets = soup.select(
        ".portlet-borderless-container"
    )

    data = (
        list(map(
            lambda portlet: _get_article_data(
                portlet, f"article{suffix}"
            ),
            portlets
        ))
        for suffix in ("p", "b", "c")
    )

    data = list(filter(
        lambda x: x,
        chain(*data)
    ))

    return data

def get_page_content(
    soup: bs4.BeautifulSoup
) -> list[dict[str, str | list]]:
    first = get_data_from_portlets_article(soup)
    second = get_data_from_portlets(soup)

    return first + second

def save(save_path: Path, urls: list[str]) -> None:
    for i, url in enumerate(urls):
        name = urlparse(url).path.strip("/").replace("/", ".")
        file_path = save_path / f"{i+1}_{name}.json"

        print(">", f"[{i+1}/{len(urls)}]", file_path)

        data = dict(
            origin=url,
            page_content=get_page_content(
                get_soup(url)
            )
        )

        save_json(file_path, data)

def resolve_sub_pages(
    base_url: str,
    sub_page_entry: dict[str] | list[str],
    on_url_resolved: Callable[[str], None]
) -> None:
    def _join_sub_page(sub_page_name: str) -> str:
        return "/".join((base_url, sub_page_name))

    def _resolve_sub_page_entry_dict(
        sub_page_entry: dict[str],
        on_url_resolved: Callable[[str], None]
    ) -> None:
        for (
            sub_page_name, child_sub_page_entry
        ) in sub_page_entry.items():
            resolve_sub_pages(
                _join_sub_page(sub_page_name),
                child_sub_page_entry,
                on_url_resolved
            )

    if isinstance(sub_page_entry, list):
        for sub_page_name in sub_page_entry:
            if isinstance(sub_page_name, str):
                on_url_resolved(
                    _join_sub_page(sub_page_name)
                )
            elif isinstance(sub_page_name, dict):
                _resolve_sub_page_entry_dict(
                    sub_page_name, on_url_resolved
                )
    elif isinstance(sub_page_entry, dict):
        _resolve_sub_page_entry_dict(
            sub_page_entry, on_url_resolved
        )

def resolve_urls(sub_pages: dict[str, list]) -> list[str]:
    urls = []

    resolve_sub_pages(BASE_URL, sub_pages, urls.append)

    return urls

def get_dump_dir_path() -> Path:
    return get_docs_root_dir_path() / "scrapped_faculty_webpages" / "raw"

def main() -> None:
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

    save_path = get_dump_dir_path()

    save(save_path, urls)

if __name__ == "__main__":
    main()
