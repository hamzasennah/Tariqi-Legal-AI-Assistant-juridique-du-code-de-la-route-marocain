from __future__ import annotations

import argparse

from _path import ROOT  # noqa: F401
from tariqi import FineCalculator


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate a likely fine and point withdrawal.")
    parser.add_argument("--infraction", required=True, help="Infraction name or keywords.")
    parser.add_argument(
        "--delay",
        default="24h",
        choices=["24h", "15j", "30j"],
        help="Payment delay used for the indicative amount.",
    )
    args = parser.parse_args()

    calculator = FineCalculator()
    result = calculator.calculate(args.infraction, delay=args.delay)

    print(result.message)
    if result.infraction:
        print(f"Infraction : {result.infraction['nom_infraction']}")
        print(f"Classe : {result.infraction['classe']}")
        print(f"Points : {result.points}")
        print(f"Source : {result.infraction['source']} - {result.infraction['document']}")
        print(f"URL : {result.infraction['source_url']}")


if __name__ == "__main__":
    main()
