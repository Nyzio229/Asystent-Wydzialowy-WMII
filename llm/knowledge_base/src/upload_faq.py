from pydantic import BaseModel

from utils import (
    get_cached_translation,
    get_docs_root_dir_path,
    upload_docs,
    translate_pl_to_en
)

class FAQEntry(BaseModel):
    answer: str
    question: str

def fetch_faq(
    with_pl: bool,
    serialize: bool
):
    def _print_head(
        char: str,
        message: str,
        n_chars: int
    ) -> None:
        print(
            f"   {char}:",
            f"{message[:n_chars]}"
            f'{"..." if len(message) > n_chars else ""}'
        )

    def _translate_faq(
        faq: list[FAQEntry]
    ) -> list[FAQEntry]:
        translated_faq: list[FAQEntry] = []

        for i, faq_entry in enumerate(faq):
            print(">", f"[{i+1}/{len(faq)}]:")

            n_chars = 100

            _print_head(
                "Q", faq_entry.question, n_chars
            )

            _print_head(
                "A", faq_entry.answer, n_chars
            )

            print("   * Tłumaczenie (pl -> en)...")

            translated_faq_entry = FAQEntry(
                question=translate_pl_to_en(
                    faq_entry.question
                ),
                answer=translate_pl_to_en(
                    faq_entry.answer
                )
            )

            translated_faq.append(translated_faq_entry)

            _print_head(
                "Tł_Q", translated_faq_entry.question, n_chars
            )

            _print_head(
                "Tł_A", translated_faq_entry.answer, n_chars
            )

            print("-" * int(n_chars*1.25))

        return translated_faq

    print("Czytanie FAQ...")

    faq_dir = get_docs_root_dir_path() / "faq"

    faq = get_cached_translation(
        pl_path=faq_dir / "pl.json",
        cache_path=faq_dir / "translated.json",
        translator=_translate_faq,
        model_type=FAQEntry,
        with_pl=with_pl,
        serialize=serialize
    )

    return faq

def main() -> None:
    faq, translated_faq = fetch_faq(
        with_pl=True,
        serialize=True
    )

    print("\nPrzesyłanie do bazy wektorowej...")

    lang_faqs = list(map(
        lambda lang_with_faq: dict(
            lang=lang_with_faq[0],
            faq=lang_with_faq[1]
        ),
        dict(
            pl=faq,
            en=translated_faq
        ).items()
    ))

    upload_docs(
        "upload_faq",
        lang_faqs=lang_faqs
    )

if __name__ == "__main__":
    main()
