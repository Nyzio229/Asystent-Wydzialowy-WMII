import re

from fetch_misc_docs import (
    get_academic_year_organization,
    get_umk_wiki_page
)

from utils import Document, upload_docs

from upload_faq import fetch_faq, FAQEntry

from fetch_scrapped_faculty_webpages import fetch_scrapped_faculty_webpages

def get_umk_wiki_page_docs() -> list[Document]:
    page = get_umk_wiki_page()

    docs = list(map(
        lambda doc: Document(
            metadata=dict(
                origin=page.url,
                abbreviations=[
                    "umk"
                ]
            ),
            page_content=doc
        ),
        re.split(
            "\n== .* ==\n", page.page_content
        )
    ))

    return docs

def get_academic_year_organization_doc() -> Document:
    ayo = get_academic_year_organization()

    doc = Document(
        metadata=dict(
            origin=ayo.remote_file_path,
            tags=[
                "Organization of the academic year"
            ]
        ),
        page_content=ayo.file_content
    )

    return doc

def get_faq_docs() -> list[Document]:
    faq = fetch_faq(
        with_pl=False,
        serialize=False
    )

    n_faq_entries = len(faq)

    def _faq_entry_to_doc(idx: int, faq_entry: FAQEntry) -> Document:
        question = faq_entry.question
        answer = faq_entry.answer

        page_content = f"Q: {question}\nA: {answer}"

        doc = Document(
            page_content=page_content,
            metadata=dict(
                origin=f"FAQ ({idx+1}/{n_faq_entries})"
            )
        )

        return doc

    faq = list(map(
        lambda pair: _faq_entry_to_doc(*pair),
        enumerate(faq)
    ))

    return faq

def main() -> None:
    downloading_texts_with_getters = [
        ("zescrapowanych danych ze stron wydziałowych", fetch_scrapped_faculty_webpages),
        ("FAQ", get_faq_docs),
        ("organizacji roku akademickiego", get_academic_year_organization_doc),
        ("strony UMK na wikipedii", get_umk_wiki_page_docs)
    ]

    print("Pobieranie:")

    docs: list[Document] = []

    for i, (text, doc_getter) in enumerate(
        downloading_texts_with_getters
    ):
        print(f"\n{i+1}. {text}...")

        doc = doc_getter()

        if isinstance(doc, Document):
            doc = [doc]

        docs += doc

    docs = list(map(
        lambda doc: doc.model_dump(),
        docs
    ))

    print("\nPrzesyłanie do bazy wektorowej...")

    upload_docs(
        "upload_rag_docs",
        docs=docs
    )

if __name__ == "__main__":
    main()
