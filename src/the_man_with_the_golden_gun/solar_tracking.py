"""Solar tracking and daily insolation model for the SOLEX mission.

The Solex mirror field follows the sun across the island sky; this module adds
the time-geometry layer of the yield model: the solar position (declination,
equation of time, elevation, azimuth), the daylight window, and the daily
energy that the field can concentrate when the tracking geometry is correct.

All formulas are standard solar-engineering results, evaluated
deterministically for a fixed latitude and day of year:

* declination and equation of time — Spencer's Fourier series
  (Spencer, 1971; cf. Duffie & Beckman 2013, ch. 1);
* daily extraterrestrial irradiation on a horizontal plane — the
  closed-form Duffie–Beckman expression with the solar hour angle at
  sunrise; a clearness factor converts it to a clear-sky resource;
* field daily thermal energy — the clear-sky insolation integrated over the
  mirror field's effective aperture (area × reflectivity) with the optical
  and heat-transfer efficiencies of :mod:`.solar_concentration`.

No random draws, no wall clock: the latitude, day of year, peak DNI and solar
constant are fixed canonical inputs.
"""

from __future__ import annotations

import math

from .solar_concentration import Mirror

__all__ = [
    "SOLEX_CLEARNESS",
    "SOLEX_DAY_OF_YEAR",
    "SOLEX_DNI_PEAK",
    "SOLEX_LATITUDE_DEG",
    "SOLEX_SOLAR_CONSTANT_W_M2",
    "beam_flux_kw_m2",
    "daily_clear_sky_insolation_kwh_m2",
    "daily_extraterrestrial_insolation_kwh_m2",
    "daylight_hours",
    "equation_of_time_min",
    "field_daily_energy_kwh",
    "solar_azimuth_deg",
    "solar_declination_deg",
    "solar_elevation_deg",
    "solar_hour_angle_deg",
    "solex_daily_profile",
    "sun_position",
]

#: Canonical SOLEX site latitude (degrees north; the island lies ~8° N).
SOLEX_LATITUDE_DEG = 8.0
#: Canonical day of year (172 = 21 June, northern solstice).
SOLEX_DAY_OF_YEAR = 172
#: Canonical peak direct normal irradiance (W/m^2), shared with the field model.
SOLEX_DNI_PEAK = 1000.0
#: Solar constant (W/m^2) — mean Earth–Sun distance.
SOLEX_SOLAR_CONSTANT_W_M2 = 1361.0
#: Clearness factor converting extraterrestrial to clear-sky insolation.
SOLEX_CLEARNESS = 0.75


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _validate_day(day_of_year: int) -> None:
    _require(isinstance(day_of_year, int) and 1 <= day_of_year <= 366, "day_of_year must be an int in [1, 366]")


def solar_declination_deg(day_of_year: int) -> float:
    """Solar declination (degrees) via Spencer's Fourier series.

    Args:
        day_of_year: 1..366 (day 1 = 1 January).

    Returns:
        Declination in degrees (≈ +23.45° at the June solstice).
    """
    _validate_day(day_of_year)
    gamma = 2.0 * math.pi * (day_of_year - 1) / 365.0
    decl_rad = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2.0 * gamma)
        + 0.000907 * math.sin(2.0 * gamma)
        - 0.002697 * math.cos(3.0 * gamma)
        + 0.00148 * math.sin(3.0 * gamma)
    )
    return math.degrees(decl_rad)


def equation_of_time_min(day_of_year: int) -> float:
    """Equation of time (minutes) via Spencer's Fourier series."""
    _validate_day(day_of_year)
    gamma = 2.0 * math.pi * (day_of_year - 1) / 365.0
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2.0 * gamma)
        - 0.040849 * math.sin(2.0 * gamma)
    )


def solar_hour_angle_deg(solar_time_h: float) -> float:
    """Solar hour angle (degrees): 0 at solar noon, 15°/hour before/after."""
    return 15.0 * (solar_time_h - 12.0)


def solar_elevation_deg(latitude_deg: float, declination_deg: float, hour_angle_deg: float) -> float:
    """Solar elevation above the horizon (degrees).

    ``sin(e) = sin(phi)sin(delta) + cos(phi)cos(delta)cos(H)``, clamped to the
    horizon so below-horizon sun returns a non-positive elevation.
    """
    phi, delta, h = (math.radians(latitude_deg), math.radians(declination_deg), math.radians(hour_angle_deg))
    sin_e = math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.cos(h)
    return math.degrees(math.asin(max(-1.0, min(1.0, sin_e))))


def solar_azimuth_deg(
    latitude_deg: float,
    declination_deg: float,
    elevation_deg: float,
    hour_angle_deg: float,
) -> float:
    """Solar azimuth (degrees from north, clockwise).

    Uses the standard ``cos(az) = (sin(delta) - sin(phi) sin(e)) /
    (cos(phi) cos(e))`` convention; when the denominator vanishes the azimuth
    is 180° (south) at solar noon sign conventions.
    """
    phi, delta, e = (math.radians(latitude_deg), math.radians(declination_deg), math.radians(elevation_deg))
    denominator = math.cos(phi) * math.cos(e)
    if abs(denominator) < 1e-9:
        return 180.0 if hour_angle_deg < 0 else 0.0
    cos_az = (math.sin(delta) - math.sin(phi) * math.sin(e)) / denominator
    az = math.degrees(math.acos(max(-1.0, min(1.0, cos_az))))
    if hour_angle_deg < 0:  # morning: azimuth east of south
        return 360.0 - az
    return az


def daylight_hours(latitude_deg: float, declination_deg: float) -> float:
    """Daylight duration (hours) from the sunrise hour angle.

    ``daylight = (2/15) * acos(-tan(phi) tan(delta))`` with the argument
    clamped: polar night → 0, polar day → 24.
    """
    argument = -math.tan(math.radians(latitude_deg)) * math.tan(math.radians(declination_deg))
    if argument >= 1.0:
        return 0.0
    if argument <= -1.0:
        return 24.0
    return (2.0 / 15.0) * math.degrees(math.acos(argument))


def beam_flux_kw_m2(dni_w_m2: float, elevation_deg: float) -> float:
    """Beam irradiance on a horizontal plane (kW/m^2): ``DNI * sin(elevation)``.

    Non-positive elevation yields zero flux (sun below the horizon).
    """
    _require(dni_w_m2 > 0, "dni_w_m2 must be positive")
    if elevation_deg <= 0.0:
        return 0.0
    return dni_w_m2 / 1000.0 * math.sin(math.radians(elevation_deg))


def daily_extraterrestrial_insolation_kwh_m2(
    latitude_deg: float,
    day_of_year: int,
    solar_constant_w_m2: float = SOLEX_SOLAR_CONSTANT_W_M2,
) -> float:
    """Daily extraterrestrial irradiation on a horizontal plane (kWh/m^2/day).

    The Duffie–Beckman closed form:

    ``H0 = (24/pi) Gsc [1 + 0.033 cos(2 pi d/365)] (cos phi cos delta sin ws
    + ws sin phi sin delta)``

    with ``ws`` the sunrise hour angle in radians.
    """
    _require(solar_constant_w_m2 > 0, "solar_constant_w_m2 must be positive")
    declination = solar_declination_deg(day_of_year)
    phi = math.radians(latitude_deg)
    delta = math.radians(declination)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(delta))))
    eccentricity = 1.0 + 0.033 * math.cos(2.0 * math.pi * day_of_year / 365.0)
    factor = math.cos(phi) * math.cos(delta) * math.sin(ws) + ws * math.sin(phi) * math.sin(delta)
    return (24.0 / math.pi) * solar_constant_w_m2 * eccentricity * factor / 1000.0


def daily_clear_sky_insolation_kwh_m2(
    latitude_deg: float,
    day_of_year: int,
    solar_constant_w_m2: float = SOLEX_SOLAR_CONSTANT_W_M2,
    clearness: float = SOLEX_CLEARNESS,
) -> float:
    """Clear-sky daily insolation (kWh/m^2/day): extraterrestrial × clearness."""
    _require(0.0 < clearness <= 1.0, "clearness must be in (0, 1]")
    return clearness * daily_extraterrestrial_insolation_kwh_m2(latitude_deg, day_of_year, solar_constant_w_m2)


def field_daily_energy_kwh(
    mirrors: tuple[Mirror, ...],
    latitude_deg: float,
    day_of_year: int,
    optical_efficiency: float = 0.9,
    heat_transfer_efficiency: float = 0.85,
    solar_constant_w_m2: float = SOLEX_SOLAR_CONSTANT_W_M2,
    clearness: float = SOLEX_CLEARNESS,
) -> float:
    """Thermal energy (kWh) the field concentrates over a clear-sky day.

    Clear-sky insolation × effective aperture (Σ area·reflectivity) × optical
    and heat-transfer efficiencies.
    """
    insolation = daily_clear_sky_insolation_kwh_m2(latitude_deg, day_of_year, solar_constant_w_m2, clearness)
    effective_aperture = sum(m.area_m2 * m.reflectivity for m in mirrors)
    return insolation * effective_aperture * optical_efficiency * heat_transfer_efficiency


def sun_position(latitude_deg: float, day_of_year: int, solar_time_h: float) -> dict[str, float]:
    """Full solar position record at a given solar time (deterministic)."""
    _require(0.0 <= solar_time_h <= 24.0, "solar_time_h must be in [0, 24]")
    declination = solar_declination_deg(day_of_year)
    hour_angle = solar_hour_angle_deg(solar_time_h)
    elevation = solar_elevation_deg(latitude_deg, declination, hour_angle)
    return {
        "declination_deg": declination,
        "equation_of_time_min": equation_of_time_min(day_of_year),
        "hour_angle_deg": hour_angle,
        "elevation_deg": elevation,
        "azimuth_deg": solar_azimuth_deg(latitude_deg, declination, elevation, hour_angle),
    }


def solex_daily_profile(step_minutes: int = 10) -> dict[str, list[float]]:
    """Hourly beam-flux profile for the canonical SOLEX site/day.

    Returns parallel ``solar_time_h`` / ``beam_kw_m2`` lists from sunrise to
    sunset (10-minute steps by default) for the deterministic daily figure.
    """
    _require(step_minutes > 0, "step_minutes must be positive")
    times: list[float] = []
    flux: list[float] = []
    for minute in range(0, 24 * 60 + 1, step_minutes):
        solar_time = minute / 60.0
        elevation = solar_elevation_deg(
            SOLEX_LATITUDE_DEG,
            solar_declination_deg(SOLEX_DAY_OF_YEAR),
            solar_hour_angle_deg(solar_time),
        )
        if elevation <= 0.0:
            continue
        times.append(round(solar_time, 4))
        flux.append(round(beam_flux_kw_m2(SOLEX_DNI_PEAK, elevation), 4))
    return {"solar_time_h": times, "beam_kw_m2": flux}
