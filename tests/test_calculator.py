from __future__ import annotations

from pathlib import Path

from tariqi.calculator import FineCalculator


ROOT = Path(__file__).resolve().parents[1]


def test_calculate_red_light_points_and_amount() -> None:
    calculator = FineCalculator(ROOT / "data" / "structured" / "infractions_maroc.csv")

    result = calculator.calculate("feu rouge", delay="24h")

    assert result.matched is True
    assert result.amount == "400"
    assert result.points == "4"
    assert result.infraction is not None
    assert "STOP" in result.infraction["nom_infraction"]


def test_calculate_unknown_infraction() -> None:
    calculator = FineCalculator(ROOT / "data" / "structured" / "infractions_maroc.csv")

    result = calculator.calculate("question sans rapport")

    assert result.matched is False
    assert result.amount is None


def test_calculate_line_continuous_from_natural_phrase() -> None:
    calculator = FineCalculator(ROOT / "data" / "structured" / "infractions_maroc.csv")

    result = calculator.calculate("si je depasses une voiture dans une ligne continu?", delay="24h")

    assert result.matched is True
    assert result.amount == "400"
    assert result.points == "4"
    assert result.infraction is not None
    assert result.infraction["id_infraction"] == "INF_015"
