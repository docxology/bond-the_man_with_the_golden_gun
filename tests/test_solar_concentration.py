"""Tests for the SOLEX solar concentration yield model (real data, no mocks)."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.solar_concentration import (
    Mirror,
    SOLEX_DNI,
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
    field_optical_power,
    mirror_optical_power,
    optimal_mirror_allocation,
    solex_heat_output_kw,
    solex_yield,
    thermal_output_kw,
)


def test_mirror_valid() -> None:
    m = Mirror(id="a", area_m2=2.0, reflectivity=0.5)
    assert m.id == "a"
    assert m.area_m2 == 2.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"id": " ", "area_m2": 1.0, "reflectivity": 0.5},  # blank id
        {"id": "a", "area_m2": 0.0, "reflectivity": 0.5},  # non-positive area
        {"id": "a", "area_m2": 1.0, "reflectivity": 1.5},  # reflectivity > 1
        {"id": "a", "area_m2": 1.0, "reflectivity": -0.1},  # reflectivity < 0
    ],
)
def test_mirror_validation(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        Mirror(**kwargs)  # type: ignore[arg-type]


def test_mirror_optical_power_value() -> None:
    m = Mirror(id="a", area_m2=2.0, reflectivity=0.5)
    assert mirror_optical_power(dni=1000.0, mirror=m) == 1000.0
    # incidence factor scales linearly
    assert mirror_optical_power(1000.0, m, incidence_factor=0.8) == 800.0


def test_mirror_optical_power_validation() -> None:
    m = Mirror(id="a", area_m2=2.0, reflectivity=0.5)
    with pytest.raises(ValueError):
        mirror_optical_power(0.0, m)
    with pytest.raises(ValueError):
        mirror_optical_power(1000.0, m, incidence_factor=0.0)


def test_field_optical_power_sum() -> None:
    total = field_optical_power(SOLEX_FIELD, SOLEX_DNI)
    expected = sum(1000.0 * m.area_m2 * m.reflectivity for m in SOLEX_FIELD)
    assert total == expected
    assert total == 250500.0
    # empty field is zero
    assert field_optical_power((), SOLEX_DNI) == 0.0


def test_thermal_output_kw_canonical() -> None:
    # 250.5 kW optical -> *0.9*0.85 = 191.6325 kW
    assert thermal_output_kw(SOLEX_FIELD, SOLEX_DNI) == pytest.approx(191.6325)
    assert solex_heat_output_kw() == pytest.approx(191.6325)


def test_thermal_output_kw_validation() -> None:
    with pytest.raises(ValueError):
        thermal_output_kw(SOLEX_FIELD, SOLEX_DNI, optical_efficiency=0.0)
    with pytest.raises(ValueError):
        thermal_output_kw(SOLEX_FIELD, SOLEX_DNI, optical_efficiency=1.5)
    with pytest.raises(ValueError):
        thermal_output_kw(SOLEX_FIELD, SOLEX_DNI, heat_transfer_efficiency=0.0)


def test_concentration_ratio_canonical() -> None:
    ratio = concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2)
    assert ratio == pytest.approx(50.1)
    assert concentration_ratio(SOLEX_FIELD, 2.0) == pytest.approx(125.25)


def test_concentration_ratio_validation() -> None:
    with pytest.raises(ValueError):
        concentration_ratio(SOLEX_FIELD, 0.0)


def test_optimal_allocation_exact_budget() -> None:
    # budget = total area -> all mirrors chosen
    chosen = optimal_mirror_allocation(SOLEX_FIELD, 300.0)
    assert set(chosen) == {"alpha", "bravo", "charlie", "delta", "echo"}
    # budget smaller than largest -> picks highest-reflectivity smaller mirror
    chosen_partial = optimal_mirror_allocation(SOLEX_FIELD, 90.0)
    assert "echo" not in chosen_partial or sum(m.area_m2 for m in SOLEX_FIELD if m.id in chosen_partial) <= 90.0


def test_optimal_allocation_validation() -> None:
    with pytest.raises(ValueError):
        optimal_mirror_allocation(SOLEX_FIELD, 0.0)


def test_optimal_allocation_exact_single_mirror_breaks() -> None:
    # budget equals alpha's area exactly: after allocating it, remaining hits 0
    # and the loop breaks before bravo.
    chosen = optimal_mirror_allocation(SOLEX_FIELD, 100.0)
    assert chosen == ("alpha",)


def test_solex_yield_record() -> None:
    record = solex_yield()
    assert record["heat_output_kw"] == pytest.approx(191.6325)
    assert record["concentration_ratio"] == pytest.approx(50.1)
    assert record["field_area_m2"] == 300.0
    assert record["dni_w_per_m2"] == 1000.0
