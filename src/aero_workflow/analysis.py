from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import math
from pathlib import Path

@dataclass(frozen=True)
class OperatingPoint:
    speed_m_s: float
    chord_m: float
    mass_kg: float
    wing_area_m2: float
    density_kg_m3: float = 1.225
    dynamic_viscosity_pa_s: float = 1.7894e-5
    speed_of_sound_m_s: float = 340.3
    gravity_m_s2: float = 9.80665
    def validate(self) -> None:
        for name, value in asdict(self).items():
            if value <= 0:
                raise ValueError(f"{name} must be positive; received {value}")

@dataclass(frozen=True)
class PolarPoint:
    alpha_deg: float
    cl: float
    cd: float
    cm: float

def load_polar(path: str | Path) -> list[PolarPoint]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = [PolarPoint(**{key: float(value) for key, value in row.items()}) for row in csv.DictReader(handle)]
    if len(rows) < 2:
        raise ValueError("polar must contain at least two rows")
    rows.sort(key=lambda point: point.cl)
    if any(b.cl <= a.cl for a, b in zip(rows, rows[1:])):
        raise ValueError("polar CL values must be unique")
    if any(point.cd <= 0 for point in rows):
        raise ValueError("polar CD values must be positive")
    return rows

def interpolate_at_cl(points: list[PolarPoint], target_cl: float) -> PolarPoint:
    if not points[0].cl <= target_cl <= points[-1].cl:
        raise ValueError(f"required CL {target_cl:.4f} is outside polar range [{points[0].cl:.4f}, {points[-1].cl:.4f}]")
    for left, right in zip(points, points[1:]):
        if left.cl <= target_cl <= right.cl:
            fraction = (target_cl - left.cl) / (right.cl - left.cl)
            return PolarPoint(left.alpha_deg + fraction * (right.alpha_deg - left.alpha_deg), target_cl, left.cd + fraction * (right.cd - left.cd), left.cm + fraction * (right.cm - left.cm))
    raise RuntimeError("interpolation interval not found")

def analyze(case: OperatingPoint, polar: list[PolarPoint]) -> dict[str, float]:
    case.validate()
    q = 0.5 * case.density_kg_m3 * case.speed_m_s**2
    weight = case.mass_kg * case.gravity_m_s2
    required_cl = weight / (q * case.wing_area_m2)
    point = interpolate_at_cl(polar, required_cl)
    lift = q * case.wing_area_m2 * point.cl
    drag = q * case.wing_area_m2 * point.cd
    return {"reynolds_number": case.density_kg_m3 * case.speed_m_s * case.chord_m / case.dynamic_viscosity_pa_s, "mach_number": case.speed_m_s / case.speed_of_sound_m_s, "dynamic_pressure_pa": q, "required_cl": required_cl, "alpha_deg": point.alpha_deg, "cd": point.cd, "cm": point.cm, "lift_n": lift, "drag_n": drag, "lift_to_drag": point.cl / point.cd, "lift_balance_error_percent": 100.0 * (lift - weight) / weight}

def grid_convergence_index(coarse: float, medium: float, fine: float, refinement_ratio: float = 2.0) -> dict[str, float]:
    if refinement_ratio <= 1:
        raise ValueError("refinement_ratio must exceed 1")
    delta_coarse, delta_fine = coarse - medium, medium - fine
    if delta_coarse == 0 or delta_fine == 0 or delta_coarse * delta_fine <= 0:
        raise ValueError("solutions must show monotonic, non-zero convergence")
    order = abs(math.log(abs(delta_coarse / delta_fine)) / math.log(refinement_ratio))
    extrapolated = fine + (fine - medium) / (refinement_ratio**order - 1)
    gci_percent = 1.25 * abs((fine - medium) / fine) / (refinement_ratio**order - 1) * 100
    return {"observed_order": order, "extrapolated_value": extrapolated, "fine_gci_percent": gci_percent}
