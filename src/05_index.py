from __future__ import annotations

from tariqi import AppConfig, build_index


if __name__ == "__main__":
    report = build_index(AppConfig.from_env())
    print(report)
