import re

from pathlib import Path

from pydantic import BaseModel

from utils import get_cached_translation, translate, upload_docs

class FaqEntry(BaseModel):
    answer: str
    question: str

FAQ_ANSWER_RE_PATTERN = r"\s*\->\s*(.*\.$)"
FAQ_QUESTION_RE_PATTERN = r"[0-9]+\. (.*\?$)"

def parse_faq_file(lines: list[str]) -> list[FaqEntry]:
    question: str = None

    faq: list[FaqEntry] = []

    for line in lines:
        match = re.search(FAQ_QUESTION_RE_PATTERN, line)

        if match:
            question = match.group(1)

            continue

        match = re.search(FAQ_ANSWER_RE_PATTERN, line)

        if match:
            answer = match.group(1)

            faq_entry = FaqEntry(
                question=question,
                answer=answer
            )

            faq.append(faq_entry)

    return faq

def fetch_faq() -> tuple[
    list[dict[str]],
    list[dict[str]]
]:
    print("Czytanie FAQ...")

    faq_file_path = Path("faq") / "pl.txt"

    with open(faq_file_path, encoding="utf8") as file:
        lines = file.readlines()

    lines = filter(lambda line: not line.isspace(), lines)

    faq = parse_faq_file(lines)

    lang_from = "pl"
    lang_to = "en-US"

    def _translate(message: str) -> str:
        return translate(message, lang_from, lang_to)

    def _print_head(char: str, message: str, n_chars: int) -> None:
        print(f"   {char}:", f'{message[:n_chars]}{"..." if len(message) > n_chars else ""}')

    def _serialize_faq_entry(
        faq_entry: FaqEntry
    ) -> dict[str, str]:
        return dict(
            question=faq_entry.question,
            answer=faq_entry.answer
        )

    translated_faq: list[FaqEntry] = []

    for i, faq_entry in enumerate(faq):
        print(">", f"[{i+1}/{len(faq)}]:")

        n_chars = 100
        _print_head("Q", faq_entry.question, n_chars)
        _print_head("A", faq_entry.answer, n_chars)

        print(f"   * Tłumaczenie ({lang_from} -> {lang_to})...")

        cache_path = faq_file_path.parent / "translated" / f"{i+1}.json"
        translated_faq_entry = get_cached_translation(
            cache_path=cache_path,
            translator=lambda: FaqEntry(
                question=_translate(faq_entry.question),
                answer=_translate(faq_entry.answer)
            ),
            serializer=_serialize_faq_entry,
            deserializer=lambda serialized: FaqEntry(
                question=serialized["question"],
                answer=serialized["answer"]
            )
        )

        _print_head("Tł_Q", translated_faq_entry.question, n_chars)
        _print_head("Tł_A", translated_faq_entry.answer, n_chars)

        translated_faq.append(translated_faq_entry)

        print("-" * int(n_chars*1.25))

    faq = list(map(_serialize_faq_entry, faq))
    translated_faq = list(map(_serialize_faq_entry, translated_faq))

    return faq, translated_faq

def main() -> None:
    faq, translated_faq = fetch_faq()

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
        "faq_upload",
        lang_faqs=[
            _make_lang_faq(faq, "pl"),
            _make_lang_faq(translated_faq, "en")
        ]
    )

if __name__ == "__main__":
    main()
