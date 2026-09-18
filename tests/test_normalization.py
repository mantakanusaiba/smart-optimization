import pytest

from app.directives.normalize import normalize_reserve, normalize_solar_factor, normalize_window


@pytest.mark.parametrize(("start", "end", "expected"), [(13,15,[13,14]),(2,5,[2,3,4]),(18,21,[18,19,20]),(11,14,[11,12,13])])
def test_windows(start, end, expected): assert normalize_window(start, end) == expected


@pytest.mark.parametrize(("value", "kind"), [(80,"reduction_percent"),(20,"remaining_percent"),(.8,"reduction_fraction"),(.2,"remaining_fraction")])
def test_solar(value, kind): assert normalize_solar_factor(value, kind) == pytest.approx(.2)


@pytest.mark.parametrize(("value", "kind"), [(50,"battery_capacity_percent"),(.5,"battery_capacity_fraction"),(100,"absolute_kwh")])
def test_reserve(value, kind): assert normalize_reserve(value, kind, 200) == pytest.approx(100)
