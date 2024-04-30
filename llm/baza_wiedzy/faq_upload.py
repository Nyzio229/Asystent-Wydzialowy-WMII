import re

from pydantic import BaseModel

from utils import translate, upload_docs

class FaqEntry(BaseModel):
    answer: str
    question: str

faq_question_re_pattern = r"[0-9]+\. (.*\?$)"
faq_answer_re_pattern = r"\s*\->\s*(.*\.$)"

def parse_faq_file(lines: list[str]) -> list[FaqEntry]:
    question: str = None

    faq: list[FaqEntry] = []

    for line in lines:
        match = re.search(faq_question_re_pattern, line)

        if match:
            question = match.group(1)

            continue

        match = re.search(faq_answer_re_pattern, line)

        if match:
            answer = match.group(1)

            faq.append(FaqEntry(
                question=question,
                answer=answer
            ))

    return faq

def main() -> None:
    faq_file_path = "../../Bazy_Danych/Ankieta"

    with open(faq_file_path, encoding="utf8") as file:
        lines = file.readlines()

    lines = filter(lambda line: not line.isspace(), lines)

    faq = parse_faq_file(lines)

    def _translate(message: str) -> str:
        return translate(message, "pl", "en-US")

    def _print_head(char: str, message: str, n_chars: int) -> None:
        print(f"   {char}:", f'{message[:n_chars]}{"..." if len(message) > n_chars else ""}')

    translated_faq: list[FaqEntry] = []

    for i, faq_entry in enumerate(faq):
        print(">", f"[{i+1}/{len(faq)}]:")

        n_chars = 100
        _print_head("Q", faq_entry.question, n_chars)
        _print_head("A", faq_entry.answer, n_chars)

        print()

        translated_faq_entry = FaqEntry(
            question=_translate(faq_entry.question),
            answer=_translate(faq_entry.answer)
        )

        translated_faq.append(translated_faq_entry)

        _print_head("TQ", translated_faq_entry.question, n_chars)
        _print_head("TA", translated_faq_entry.answer, n_chars)

        print("-" * int(n_chars*1.25))

    upload_docs(
        "faq_upload",
        faq=translated_faq,
        lang="en"
    )

    upload_docs(
        "faq_upload",
        faq=faq,
        lang="pl"
    )

if __name__ == "__main__":
    main()
