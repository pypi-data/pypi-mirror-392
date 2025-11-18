import pytest
from datetime import date
from lka_nic_decoder import decode_nic, nic_to_date, parse_nic_base, DEFAULT_NIC_DAY_OFFSET

def test_parse_old_nic():
    nic_type, year, raw = parse_nic_base("912680444V")
    assert nic_type == "Old NIC"
    assert year == 1991
    assert raw == 268

def test_decode_old_male():
    info = decode_nic("912680444V")
    assert info.gender == "Male"
    assert info.birth_year == 1991
    assert info.birth_date == date(1991, 9, 24)

def test_decode_new_female():
    # Hypothetical new female NIC: adjust for testing shape
    nic = "199253600001"  # YYYYDDDxxxx, DDD > 500 for female
    info = decode_nic(nic)
    assert info.nic_type == "New NIC"
    assert isinstance(info.birth_date, date)

def test_nic_to_date_offset_variation():
    d = nic_to_date(1991, 268, offset=DEFAULT_NIC_DAY_OFFSET)
    assert d == date(1991, 9, 24)

def test_invalid_nic_length():
    import pytest
    with pytest.raises(ValueError):
        parse_nic_base("12345")
