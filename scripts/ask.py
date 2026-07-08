from __future__ import annotations

import argparse

from _path import ROOT  # noqa: F401
from tariqi import AppConfig, TariqiAssistant


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask Tariqi Legal AI a legal road-code question.")
    parser.add_argument("question", nargs="+", help="Question to ask.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks.")
    args = parser.parse_args()

    question = " ".join(args.question)
    assistant = TariqiAssistant(AppConfig.from_env())
    answer = assistant.ask(question, top_k=args.top_k)
    print(answer.to_markdown())


if __name__ == "__main__":
    main()
