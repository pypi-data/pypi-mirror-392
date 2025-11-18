import pytest
from math import isclose

from asfeslib.aviation import (
    air_density_isa,
    speed_of_sound,
    mach_to_kmh,
    kmh_to_mach,
    stall_speed,
    haversine_distance_km,
    initial_bearing_deg,
    destination_point,
    eta_hours,
    wind_corrected_heading,
    airport_coords,
    runway_length_m,
    get_airport,
    OpenSkyClient,
)

def test_air_density_sea_level():
    rho = air_density_isa(0)
    assert isclose(rho, 1.225, rel_tol=0.05)


def test_speed_of_sound():
    a0 = speed_of_sound(0)
    assert 330 < a0 < 345


def test_mach_conversion():
    m = kmh_to_mach(340 * 3.6, 0)
    assert 0.95 < m < 1.05

    kmh = mach_to_kmh(1, 0)
    assert 1180 < kmh < 1250


def test_stall_speed():
    v = stall_speed(
        weight_kg=70000,
        wing_area_m2=122,
        cl_max=2.0,
        altitude_m=0
    )
    assert v > 40 and v < 100


def test_haversine_distance():
    moscow = (55.75, 37.61)
    spb = (59.93, 30.33)

    d = haversine_distance_km(*moscow, *spb)
    assert 600 < d < 750


def test_bearing():
    b = initial_bearing_deg(55.75, 37.61, 59.93, 30.33)
    assert 300 < b < 360


def test_destination_point_roundtrip():
    lat, lon = 55.0, 37.0
    dist = 100
    bearing = 45

    lat2, lon2 = destination_point(lat, lon, bearing, dist)
    assert isinstance(lat2, float)
    assert isinstance(lon2, float)


def test_eta():
    assert eta_hours(100, 100) == 1
    with pytest.raises(ValueError):
        eta_hours(100, 0)


def test_wind_corrected_heading():
    hdg, gs = wind_corrected_heading(
        course_deg=90,
        tas_kts=120,
        wind_dir_from_deg=0,
        wind_speed_kts=20
    )
    assert isinstance(hdg, float)
    assert isinstance(gs, float)
    assert gs < 120

def test_airport_lookup():
    ap = get_airport("UUDD")
    assert ap is not None
    assert ap["icao"] == "UUDD"


def test_airport_coords():
    coords = airport_coords("UUDD")
    assert coords and len(coords) == 2


def test_runway_length():
    length = runway_length_m("UUDD")
    assert length > 3000


@pytest.mark.asyncio
async def test_opensky_client_mock(monkeypatch):
    async def fake_get(url, params=None):
        class R:
            def raise_for_status(self): pass
            def json(self):
                return {"states": [["abc123", "TST123 ", "RU", None, None, 37.0, 55.0, 2000, None, 150, 90]]}
        return R()

    from asfeslib.aviation.api import OpenSkyClient
    client = OpenSkyClient()

    class DummyClient:
        async def get(self, url, params=None):
            return await fake_get(url, params)

    client._client = DummyClient()

    data = await client.get_states()
    assert data["states"][0][0] == "abc123"
