from __future__ import annotations
import json
from pathlib import Path
import sys
from .analysis import OperatingPoint, analyze, grid_convergence_index, load_polar

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m aero_workflow.cli CASE.json")
    case_path = Path(sys.argv[1])
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    polar_path = case_path.parent / payload.pop("polar_file")
    convergence = payload.pop("convergence_values", None)
    report: dict[str, object] = {"analysis": analyze(OperatingPoint(**payload), load_polar(polar_path))}
    if convergence:
        report["convergence"] = grid_convergence_index(*convergence)
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
