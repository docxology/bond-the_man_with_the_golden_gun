"""Tests for the SOLEX solar-tracking / daily-insolation model (real math)."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.solar_concentration import SOLEX_FIELD
from the_man_with_the_golden_gun.solar_tracking import (
    SOLEX_DAY_OF_YEAR,
    SOLEX_DNI_PEAK,
    SOLEX_LATITUDE_DEG,
    beam_flux_kw_m2,
    daily_clear_sky_insolation_kwh_m2,
    daily_extraterrestrial_insolation_kwh_m2,
    daylight_hours,
    equation_of_time_min,
    field_daily_energy_kwh,
    solar_azimuth_deg,
    solar_declination_deg,
    solar_elevation_deg,
    solar_hour_angle_deg,
    solex_daily_profile,
    sun_position,
)


def test_declination_solstices() -> None:
    # Spencer series: ~+23.45° at the June solstice, ~-23.45° in December.
    assert solar_declination_deg(172) == pytest.approx(23.45, abs=0.05)
    assert solar_declination_deg(355) == pytest.approx(-23.4, abs=0.2)


def test_declination_validation() -> None:
    with pytest.raises(ValueError):
        solar_declination_deg(0)
    with pytest.raises(ValueError):
        solar_declination_deg(367)


def test_equation_of_time() -> None:
    assert equation_of_time_min(172) == pytest.approx(-1.33, abs=0.05)


def test_hour_angle() -> None:
    assert solar_hour_angle_deg(12.0) == pytest.approx(0.0)
    assert solar_hour_angle_deg(6.0) == pytest.approx(-90.0)
    assert solar_hour_angle_deg(18.0) == pytest.approx(90.0)


def test_elevation_noon_solstice() -> None:
    decl = solar_declination_deg(172)
    elevation = solar_elevation_deg(8.0, decl, 0.0)
    assert elevation == pytest.approx(74.55, abs=0.1)
    # below-horizon: midnight hour angle 180° -> negative elevation
    assert solar_elevation_deg(8.0, decl, 180.0) < 0.0


def test_azimuth_conventions() -> None:
    decl = solar_declination_deg(172)
    # solar noon: sun due north when declination > latitude
    assert solar_azimuth_deg(8.0, decl, 74.55, 0.0) == pytest.approx(0.0, abs=1.0)
    # morning azimuth east of south -> in (270, 360)
    morning_elevation = solar_elevation_deg(8.0, decl, -45.0)
    morning_az = solar_azimuth_deg(8.0, decl, morning_elevation, -45.0)
    assert 270.0 < morning_az < 360.0
    # degenerate denominator branch (elevation ~90°): sign of hour angle decides
    assert solar_azimuth_deg(8.0, decl, 90.0, 5.0) == 0.0
    assert solar_azimuth_deg(8.0, decl, 90.0, -5.0) == 180.0


def test_daylight_hours() -> None:
    decl = solar_declination_deg(172)
    assert daylight_hours(8.0, decl) == pytest.approx(12.47, abs=0.05)
    assert daylight_hours(80.0, decl) == pytest.approx(24.0)  # polar day
    assert daylight_hours(-80.0, decl) == pytest.approx(0.0)  # polar night


def test_beam_flux() -> None:
    assert beam_flux_kw_m2(1000.0, 90.0) == pytest.approx(1.0)
    assert beam_flux_kw_m2(1000.0, 0.0) == 0.0
    assert beam_flux_kw_m2(1000.0, -10.0) == 0.0
    with pytest.raises(ValueError):
        beam_flux_kw_m2(0.0, 45.0)


def test_extraterrestrial_insolation() -> None:
    assert daily_extraterrestrial_insolation_kwh_m2(8.0, 172) == pytest.approx(10.03, abs=0.05)
    with pytest.raises(ValueError):
        daily_extraterrestrial_insolation_kwh_m2(8.0, 172, solar_constant_w_m2=0.0)


def test_clear_sky_insolation() -> None:
    assert daily_clear_sky_insolation_kwh_m2(8.0, 172) == pytest.approx(7.52, abs=0.05)
    with pytest.raises(ValueError):
        daily_clear_sky_insolation_kwh_m2(8.0, 172, clearness=0.0)
    with pytest.raises(ValueError):
        daily_clear_sky_insolation_kwh_m2(8.0, 172, clearness=1.5)


def test_field_daily_energy() -> None:
    energy = field_daily_energy_kwh(SOLEX_FIELD, 8.0, 172)
    assert energy == pytest.approx(1441.7, abs=0.5)
    assert field_daily_energy_kwh((), 8.0, 172) == 0.0


def test_sun_position_record() -> None:
    position = sun_position(8.0, 172, 12.0)
    assert position["hour_angle_deg"] == pytest.approx(0.0)
    assert position["elevation_deg"] == pytest.approx(74.55, abs=0.1)
    with pytest.raises(ValueError):
        sun_position(8.0, 172, 24.5)
    with pytest.raises(ValueError):
        sun_position(8.0, 172, -1.0)


def test_daily_profile_shape() -> None:
    profile = solex_daily_profile()
    times = profile["solar_time_h"]
    flux = profile["beam_kw_m2"]
    assert times and len(times) == len(flux)
    assert all(f > 0.0 for f in flux)
    assert times[0] > 5.0  # sunrise after 05:00 at 8°N solstice
    assert times[-1] < 19.0
    # noon horizontal beam = DNI * sin(noon elevation ≈ 74.55°) ≈ 0.964 kW/m²
    assert max(flux) == pytest.approx(0.964, abs=0.01)
    with pytest.raises(ValueError):
        solex_daily_profile(step_minutes=0)


def test_canonical_constants() -> None:
    assert SOLEX_LATITUDE_DEG == 8.0
    assert SOLEX_DAY_OF_YEAR == 172
    assert SOLEX_DNI_PEAK == 1000.0
