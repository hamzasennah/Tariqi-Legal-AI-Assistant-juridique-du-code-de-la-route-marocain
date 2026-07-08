from __future__ import annotations

import sys

from tariqi import AppConfig
from tariqi.retriever import Retriever


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Combien de points pour un feu rouge ?"
    chunks = Retriever(AppConfig.from_env()).retrieve(question)
    for item in chunks:
        print(item.source_line())
