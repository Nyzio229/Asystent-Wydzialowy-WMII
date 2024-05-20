from pathlib import Path

from pydantic import BaseModel

from utils import get_cached_translation, translate, upload_docs

class FAQEntry(BaseModel):
    answer: str
    question: str

def fetch_faq(
    with_pl: bool,
    serialize: bool
):
    print("Czytanie FAQ...")

    faq_dir = Path("faq")

    lang_from = "pl"
    lang_to = "en-US"

    def _translate(message: str) -> str:
        return translate(message, lang_from, lang_to)

    def _print_head(char: str, message: str, n_chars: int) -> None:
        print(
            f"   {char}:",
            f"{message[:n_chars]}"
            f'{"..." if len(message) > n_chars else ""}'
        )

    def _translate_faq(faq: list[FAQEntry]) -> list[FAQEntry]:
        translated_faq: list[FAQEntry] = []

        for i, faq_entry in enumerate(faq):
            print(">", f"[{i+1}/{len(faq)}]:")

            n_chars = 100
            _print_head("Q", faq_entry.question, n_chars)
            _print_head("A", faq_entry.answer, n_chars)

            print(f"   * Tłumaczenie ('{lang_from}' -> '{lang_to}')...")

            translated_faq_entry = FAQEntry(
                question=_translate(faq_entry.question),
                answer=_translate(faq_entry.answer)
            )

            translated_faq.append(translated_faq_entry)

            _print_head("Tł_Q", translated_faq_entry.question, n_chars)
            _print_head("Tł_A", translated_faq_entry.answer, n_chars)

            print("-" * int(n_chars*1.25))

        return translated_faq

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

    def _make_lang_faq(
        faq: list[dict[str]],
        lang: str
    ) -> dict[str]:
        return dict(
            faq=faq,
            lang=lang
        )

    print("\nPrzesyłanie do bazy wektorowej...")

    upload_docs(
        "upload_faq",
        lang_faqs=[
            _make_lang_faq(faq, "pl"),
            _make_lang_faq(translated_faq, "en")
        ]
    )

if __name__ == "__main__":
    main()
