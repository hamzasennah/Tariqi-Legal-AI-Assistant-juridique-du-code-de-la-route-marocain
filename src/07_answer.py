from __future__ import annotations

import sys

from tariqi import AppConfig, TariqiAssistant


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Combien de points pour un feu rouge ?"
    print(TariqiAssistant(AppConfig.from_env()).ask(question).to_markdown())
