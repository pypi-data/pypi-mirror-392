from math import pi

import pytest

from asfeslib.utils.conversions import (
    Length,
    Mass,
    Time,
    Temperature,
    Area,
    Volume,
    Speed,
    Energy,
    Pressure,
    Data,
    Angle,
    Electricity,
    Math as ConvMath,
    Mechanics,
    Finance,
    Radio,
    Geophysics,
    list_categories,
    list_functions,
    get_converter,
    get_function,
)


class TestLength:
    @pytest.mark.parametrize(
        "m, km",
        [
            (0, 0),
            (1000, 1),
            (2500, 2.5),
        ],
    )
    def test_meters_km(self, m, km):
        assert Length.meters_to_km(m) == pytest.approx(km)
        assert Length.km_to_m(km) == pytest.approx(m)

    def test_inches_cm(self):
        assert Length.inches_to_cm(1) == pytest.approx(2.54)
        assert Length.cm_to_inches(2.54) == pytest.approx(1)

    def test_miles_km(self):
        assert Length.miles_to_km(1) == pytest.approx(1.60934, rel=1e-6)
        assert Length.km_to_miles(1.60934) == pytest.approx(1, rel=1e-6)


class TestMass:
    def test_kg_g(self):
        assert Mass.kg_to_g(1.5) == 1500
        assert Mass.g_to_kg(1500) == 1.5

    def test_kg_lb_roundtrip(self):
        kg = 73.2
        lb = Mass.kg_to_lb(kg)
        assert Mass.lb_to_kg(lb) == pytest.approx(kg, rel=1e-6)

    def test_kg_tons(self):
        assert Mass.kg_to_tons(1000) == 1
        assert Mass.tons_to_kg(1) == 1000


class TestTime:
    def test_sec_min(self):
        assert Time.sec_to_min(120) == 2
        assert Time.min_to_sec(2) == 120

    def test_hours_days(self):
        assert Time.hours_to_days(24) == 1
        assert Time.days_to_hours(1) == 24


class TestTemperature:
    def test_c_f_roundtrip(self):
        c = 25
        f = Temperature.c_to_f(c)
        assert Temperature.f_to_c(f) == pytest.approx(c, rel=1e-6)

    def test_c_k_roundtrip(self):
        c = -10
        k = Temperature.c_to_k(c)
        assert Temperature.k_to_c(k) == pytest.approx(c)


class TestArea:
    def test_m2_km2(self):
        assert Area.m2_to_km2(1_000_000) == 1
        assert Area.km2_to_m2(1) == 1_000_000

    def test_m2_cm2(self):
        assert Area.m2_to_cm2(1) == 10_000
        assert Area.cm2_to_m2(10_000) == 1

    def test_acres_m2(self):
        ac = 1.0
        m2 = Area.acres_to_m2(ac)
        assert Area.m2_to_acres(m2) == pytest.approx(ac, rel=1e-6)


class TestVolume:
    def test_l_ml(self):
        assert Volume.liters_to_ml(1.23) == 1230
        assert Volume.ml_to_liters(1230) == 1.23

    def test_l_m3(self):
        assert Volume.liters_to_m3(1000) == 1
        assert Volume.m3_to_liters(1) == 1000

    def test_l_gallons_roundtrip(self):
        l = 10
        g = Volume.liters_to_gallons(l)
        assert Volume.gallons_to_liters(g) == pytest.approx(l, rel=1e-6)


class TestSpeed:
    def test_mps_kmph(self):
        assert Speed.mps_to_kmph(10) == 36
        assert Speed.kmph_to_mps(36) == 10

    def test_mph_kmph(self):
        mph = 60
        kmph = Speed.mph_to_kmph(mph)
        assert kmph == pytest.approx(96.5604, rel=1e-4)
        assert Speed.kmph_to_mph(kmph) == pytest.approx(mph, rel=1e-6)


class TestEnergy:
    def test_j_cal(self):
        assert Energy.cal_to_joules(1) == pytest.approx(4.184)
        assert Energy.joules_to_cal(4.184) == pytest.approx(1, rel=1e-6)

    def test_kwh_j(self):
        assert Energy.kwh_to_joules(1) == 3_600_000
        assert Energy.joules_to_kwh(3_600_000) == 1


class TestPressure:
    def test_atm_pa(self):
        assert Pressure.atm_to_pa(1) == 101_325
        assert Pressure.pa_to_atm(101_325) == pytest.approx(1)

    def test_bar_pa(self):
        assert Pressure.bar_to_pa(1.2) == 120_000
        assert Pressure.pa_to_bar(120_000) == 1.2


class TestData:
    def test_bytes_kb(self):
        assert Data.bytes_to_kb(1024) == 1
        assert Data.kb_to_bytes(1) == 1024

    def test_kb_mb(self):
        assert Data.kb_to_mb(2048) == 2
        assert Data.mb_to_kb(2) == 2048

    def test_mb_gb(self):
        assert Data.mb_to_gb(2048) == 2
        assert Data.gb_to_mb(2) == 2048


class TestAngle:
    def test_deg_rad_roundtrip(self):
        deg = 180
        rad = Angle.deg_to_rad(deg)
        assert rad == pytest.approx(pi, rel=1e-6)
        assert Angle.rad_to_deg(rad) == pytest.approx(deg, rel=1e-6)


class TestElectricity:
    def test_volts_millivolts(self):
        assert Electricity.volts_to_millivolts(1.23) == 1230
        assert Electricity.millivolts_to_volts(1230) == 1.23

    def test_amps_milliamps(self):
        assert Electricity.amps_to_milliamps(0.5) == 500
        assert Electricity.milliamps_to_amps(500) == 0.5

    def test_ohm_law(self):
        u = Electricity.ohm_law_u(2, 10)
        assert u == 20
        assert Electricity.ohm_law_i(20, 10) == 2
        assert Electricity.ohm_law_r(20, 2) == 10


class TestMath:
    def test_percent_of(self):
        assert ConvMath.percent_of(200, 15) == 30

    def test_percent_change(self):
        assert ConvMath.percent_change(100, 120) == 20

    def test_add_subtract_percent(self):
        assert ConvMath.add_percent(100, 10) == pytest.approx(110)
        assert ConvMath.subtract_percent(100, 10) == pytest.approx(90)

    def test_means(self):
        assert ConvMath.average(2, 4) == 3
        assert ConvMath.geometric_mean(2, 8) == pytest.approx(4)
        assert ConvMath.harmonic_mean(2, 6) == pytest.approx(3)


class TestMechanics:
    def test_newton_kgf(self):
        n = 9.80665
        kgf = Mechanics.newton_to_kgf(n)
        assert kgf == pytest.approx(1, rel=1e-6)
        assert Mechanics.kgf_to_newton(kgf) == pytest.approx(n, rel=1e-6)

    def test_watts_hp(self):
        assert Mechanics.watts_to_hp(745.7) == pytest.approx(1, rel=1e-4)
        assert Mechanics.hp_to_watts(1) == pytest.approx(745.7, rel=1e-4)

    def test_knots_mps(self):
        mps = 10
        knots = Mechanics.mps_to_knots(mps)
        assert Mechanics.knots_to_mps(knots) == pytest.approx(mps, rel=1e-6)


class TestFinance:
    def test_rub_kop(self):
        assert Finance.rub_to_kop(1.5) == 150
        assert Finance.kop_to_rub(150) == 1.5

    def test_usd_cents(self):
        assert Finance.usd_to_cents(2.5) == 250
        assert Finance.cents_to_usd(250) == 2.5

    def test_vat(self):
        assert Finance.vat_amount(120, vat=20) == 24

    def test_loan_monthly_payment_zero_rate(self):
        payment = Finance.loan_monthly_payment(1200, 0, 1)
        assert payment == pytest.approx(100)

    def test_margin(self):
        assert Finance.profit_from_margin(100, 30) == 30
        assert Finance.final_price_with_margin(100, 30) == 130


class TestRadio:
    def test_freq_units(self):
        assert Radio.hz_to_khz(1000) == 1
        assert Radio.khz_to_hz(1) == 1000
        assert Radio.khz_to_mhz(1000) == 1
        assert Radio.mhz_to_khz(1) == 1000
        assert Radio.mhz_to_ghz(1000) == 1
        assert Radio.ghz_to_mhz(1) == 1000

    def test_wave_freq(self):
        f = 100e6  # 100 MHz
        lam = Radio.wavelength_from_freq(f)
        assert Radio.freq_from_wavelength(lam) == pytest.approx(f, rel=1e-6)

    def test_dbm_mw(self):
        assert Radio.dbm_to_mw(0) == pytest.approx(1)
        assert Radio.dbm_to_mw(10) == pytest.approx(10)
        assert Radio.mw_to_dbm(1) == pytest.approx(0)
        assert Radio.mw_to_dbm(10) == pytest.approx(10)

        with pytest.raises(ValueError):
            Radio.mw_to_dbm(0)


class TestGeophysics:
    def test_density(self):
        assert Geophysics.density_mass(0.5, 1000) == 500
        assert Geophysics.density_volume(500, 1000) == 0.5

    def test_gforce(self):
        assert Geophysics.gforce_from_acc(9.80665) == pytest.approx(1)
        assert Geophysics.acc_from_gforce(1) == pytest.approx(9.80665)

    def test_rpm(self):
        rad = Geophysics.rpm_to_rad_per_s(60)
        assert Geophysics.rad_per_s_to_rpm(rad) == pytest.approx(60, rel=1e-6)

    def test_lux_lm(self):
        lm = Geophysics.lux_to_lm(2, 100)
        assert lm == 200
        assert Geophysics.lm_to_lux(lm, 2) == 100


class TestHelpers:
    def test_list_categories(self):
        cats = list_categories()
        assert "length" in cats
        assert "finance" in cats

    def test_list_functions(self):
        data = list_functions("length")
        assert "length" in data
        assert "meters_to_km" in data["length"]

    def test_get_converter_and_function(self):
        cls = get_converter("length")
        assert cls is Length

        func = get_function("length", "meters_to_km")
        assert func(1000) == 1
