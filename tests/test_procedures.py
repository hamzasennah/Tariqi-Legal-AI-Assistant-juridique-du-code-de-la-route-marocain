from __future__ import annotations

from pathlib import Path

from tariqi.procedures import ProcedureGuide


ROOT = Path(__file__).resolve().parents[1]


def test_match_declaration_procedure() -> None:
    guide = ProcedureGuide(ROOT / "data" / "structured" / "procedures.json")

    procedure = guide.match("Je n'étais pas le conducteur du véhicule")

    assert procedure is not None
    assert procedure["id"] == "declarer_autre_conducteur"


def test_match_reclamation_procedure() -> None:
    guide = ProcedureGuide(ROOT / "data" / "structured" / "procedures.json")

    procedure = guide.match("Je veux contester une contravention radar")

    assert procedure is not None
    assert procedure["id"] == "reclamer_contravention"
