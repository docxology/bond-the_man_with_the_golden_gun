"""Solar concentration yield model for the SOLEX mission.

The Solex agitator concentrates sunlight from a field of tracking mirrors
(heliostats) onto a central receiver to produce heat. This module is the pure,
infrastructure-free domain core: it models a mirror field, computes the optical
power captured and the resulting thermal (heat) output, quantifies the
concentration ratio at the receiver, and solves the canonical resource problem
of *allocating a mirror-area budget to the highest-yield mirrors*.

Everything here is deterministic — fixed reflectivities, fixed geometry, and a
greedy allocation that is provably optimal for the fractional budget problem
(maximise total heat subject to an area budget when yield-per-area is exactly
the reflectivity). No random draws and no wall-clock dependence.

Manual reference (film): the silent solar-array -> heat conversion that powers
the Solex agitator. The numbers below are the canonical SOLEX field.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Mirror",
    "SOLEX_DNI",
    "SOLEX_FIELD",
    "SOLEX_RECEIVER_AREA_M2",
    "concentration_ratio",
    "field_optical_power",
    "mirror_optical_power",
    "optimal_mirror_allocation",
    "solex_heat_output_kw",
    "solex_yield",
    "thermal_output_kw",
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Mirror:
    """A single tracking heliostat: area and specular reflectivity.

    ``reflectivity`` is in [0, 1]; ``area_m2`` must be positive.
    """

    id: str
    area_m2: float
    reflectivity: float

    def __post_init__(self) -> None:
        _require(bool(self.id.strip()), "Mirror.id must be a non-empty string")
        _require(self.area_m2 > 0, f"Mirror.area_m2 must be positive, got {self.area_m2}")
        _require(
            0.0 <= self.reflectivity <= 1.0,
            f"Mirror.reflectivity must be in [0, 1], got {self.reflectivity}",
        )


#: Canonical direct normal irradiance (W/m^2) for the SOLEX field.
SOLEX_DNI = 1000.0

#: Receiver aperture area (m^2) for concentration-ratio reporting.
SOLEX_RECEIVER_AREA_M2 = 5.0

#: Canonical SOLEX mirror field — total area 300 m^2.
SOLEX_FIELD: tuple[Mirror, ...] = (
    Mirror(id="alpha", area_m2=100.0, reflectivity=0.90),
    Mirror(id="bravo", area_m2=80.0, reflectivity=0.85),
    Mirror(id="charlie", area_m2=60.0, reflectivity=0.80),
    Mirror(id="delta", area_m2=50.0, reflectivity=0.75),
    Mirror(id="echo", area_m2=10.0, reflectivity=0.70),
)


def mirror_optical_power(
    dni: float,
    mirror: Mirror,
    incidence_factor: float = 1.0,
) -> float:
    """Optical power (W) delivered by one mirror: ``dni * area * reflectivity``.

    Args:
        dni: Direct normal irradiance (W/m^2).
        mirror: The mirror to evaluate.
        incidence_factor: Cosine/incidence loss in [0, 1] (default 1.0).

    Raises:
        ValueError: if ``dni`` or ``incidence_factor`` is non-positive.
    """
    _require(dni > 0, "dni must be positive")
    _require(incidence_factor > 0, "incidence_factor must be positive")
    return dni * mirror.area_m2 * mirror.reflectivity * incidence_factor


def field_optical_power(
    mirrors: tuple[Mirror, ...],
    dni: float,
    incidence_factor: float = 1.0,
) -> float:
    """Total optical power (W) captured across the whole mirror field."""
    return sum(mirror_optical_power(dni, mirror, incidence_factor) for mirror in mirrors)


def thermal_output_kw(
    mirrors: tuple[Mirror, ...],
    dni: float,
    optical_efficiency: float = 0.9,
    heat_transfer_efficiency: float = 0.85,
) -> float:
    """Thermal (heat) output in kilowatts delivered to the working fluid.

    ``optical_efficiency`` accounts for receiver-intercept losses and
    ``heat_transfer_efficiency`` for losses in the heat exchanger; both must
    lie in (0, 1].
    """
    _require(0.0 < optical_efficiency <= 1.0, "optical_efficiency must be in (0, 1]")
    _require(0.0 < heat_transfer_efficiency <= 1.0, "heat_transfer_efficiency must be in (0, 1]")
    optical_kw = field_optical_power(mirrors, dni) / 1000.0
    return optical_kw * optical_efficiency * heat_transfer_efficiency


def concentration_ratio(
    mirrors: tuple[Mirror, ...],
    receiver_area_m2: float,
    dni: float = SOLEX_DNI,
) -> float:
    """Dimensionless flux concentration ratio at the receiver aperture.

    Defined as optical power per receiver area divided by ``dni``; because the
    ``dni`` factor cancels, it equals the effective mirrored area per receiver
    area (weighted by reflectivity and incidence).
    """
    _require(receiver_area_m2 > 0, "receiver_area_m2 must be positive")
    optical_w = field_optical_power(mirrors, dni)
    return optical_w / (dni * receiver_area_m2)


def optimal_mirror_allocation(
    candidates: tuple[Mirror, ...],
    budget_m2: float,
    dni: float = SOLEX_DNI,
) -> tuple[str, ...]:
    """Greedily allocate an area budget to the highest-yield mirrors.

    Yield-per-area of a mirror is exactly its reflectivity, so the fractional
    knapsack optimum is achieved by taking mirrors in descending reflectivity
    (ties broken by larger area first) up to the area budget. Returns the
    selected mirror ids in allocation order.
    """
    _require(budget_m2 > 0, "budget_m2 must be positive")
    ordered = sorted(candidates, key=lambda m: (m.reflectivity, m.area_m2), reverse=True)
    selected: list[str] = []
    remaining = budget_m2
    for mirror in ordered:
        if remaining <= 0:
            break
        if mirror.area_m2 <= remaining:
            selected.append(mirror.id)
            remaining -= mirror.area_m2
    return tuple(selected)


def solex_heat_output_kw(optical_efficiency: float = 0.9, heat_transfer_efficiency: float = 0.85) -> float:
    """Heat output (kW) of the canonical SOLEX field under :data:`SOLEX_DNI`."""
    return thermal_output_kw(
        SOLEX_FIELD,
        SOLEX_DNI,
        optical_efficiency=optical_efficiency,
        heat_transfer_efficiency=heat_transfer_efficiency,
    )


def solex_yield() -> dict[str, float | str]:
    """Canonical SOLEX yield record (deterministic dict for outcome reporting).

    Returns a JSON-serialisable mapping of the field's optical power, thermal
    output, concentration ratio, total area, and DNI.
    """
    optical_kw = field_optical_power(SOLEX_FIELD, SOLEX_DNI) / 1000.0
    return {
        "dni_w_per_m2": SOLEX_DNI,
        "field_area_m2": sum(m.area_m2 for m in SOLEX_FIELD),
        "optical_power_kw": round(optical_kw, 4),
        "heat_output_kw": round(solex_heat_output_kw(), 4),
        "concentration_ratio": round(concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2), 2),
        "receiver_area_m2": SOLEX_RECEIVER_AREA_M2,
    }
