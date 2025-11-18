import pytest
from asfeslib.aviation import OpenSkyClient

pytestmark = pytest.mark.live


def _skip_if_rate_limited(resp_text: str):
    if "rate" in resp_text.lower() or "429" in resp_text:
        pytest.skip("OpenSky: rate limit reached.")


@pytest.mark.asyncio
async def test_opensky_live_some_traffic():
    async with OpenSkyClient() as sky:
        try:
            data = await sky.get_states()
        except Exception as e:
            _skip_if_rate_limited(str(e))
            raise

        states = data.get("states") or []
        assert isinstance(states, list)


@pytest.mark.asyncio
async def test_opensky_live_area_moscow():
    async with OpenSkyClient() as sky:
        try:
            planes = await sky.live_area(
                min_lat=54.0,
                min_lon=35.0,
                max_lat=57.0,
                max_lon=39.0,
            )
        except Exception as e:
            _skip_if_rate_limited(str(e))
            raise

        assert isinstance(planes, list)
        for p in planes:
            assert "icao24" in p
            assert "lat" in p
            assert "lon" in p


@pytest.mark.asyncio
async def test_opensky_live_icao_filter():
    async with OpenSkyClient() as sky:
        try:
            data = await sky.get_states(icao24="abc123")
        except Exception as e:
            _skip_if_rate_limited(str(e))
            raise

        assert "states" in data
        assert isinstance(data["states"], list)
