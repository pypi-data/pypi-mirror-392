from dataclasses import dataclass
from datetime import date, datetime, timedelta
import re
from typing import Tuple

__all__ = [
    "NICInfo",
    "is_valid_nic",
    "parse_nic_base",
    "nic_to_date",
    "decode_nic",
    "DEFAULT_NIC_DAY_OFFSET",
]

DEFAULT_NIC_DAY_OFFSET = 2

@dataclass(frozen=True)
class NICInfo:
    nic_type: str
    gender: str
    birth_year: int
    raw_day_code: int
    day_code: int
    birth_date: date

    def __repr__(self) -> str:
        return (
            f"NICInfo(nic_type={self.nic_type!r}, gender={self.gender!r}, "
            f"birth_year={self.birth_year}, raw_day_code={self.raw_day_code}, "
            f"day_code={self.day_code}, birth_date={self.birth_date.isoformat()})"
        )

def is_valid_nic(nic: str) -> bool:
    nic = nic.strip()
    if len(nic) == 10:
        return bool(re.match(r"^\d{5}\w{5}$", nic, flags=re.IGNORECASE))
    if len(nic) == 12:
        return nic.isdigit()
    return False

def parse_nic_base(nic: str) -> Tuple[str, int, int]:
    nic = nic.strip()
    if len(nic) == 10:
        try:
            year_part = int(nic[0:2])
            raw_day_code = int(nic[2:5])
        except ValueError:
            raise ValueError("Invalid old NIC: expected digits in positions 1-5.")
        birth_year = 2000 + year_part if 0 <= year_part <= 25 else 1900 + year_part
        return "Old NIC", birth_year, raw_day_code
    elif len(nic) == 12:
        if not nic.isdigit():
            raise ValueError("Invalid new NIC: expected 12 digits.")
        birth_year = int(nic[0:4])
        raw_day_code = int(nic[4:7])
        return "New NIC", birth_year, raw_day_code
    else:
        raise ValueError("Invalid NIC length; expected 10 (old) or 12 (new).")

def nic_to_date(birth_year: int, day_code: int, offset: int = DEFAULT_NIC_DAY_OFFSET) -> date:
    day_of_year = day_code - offset
    start = datetime(birth_year, 1, 1)
    try:
        return (start + timedelta(days=day_of_year)).date()
    except OverflowError as exc:
        raise ValueError("Computed date out of range") from exc

def decode_nic(nic: str, offset: int = DEFAULT_NIC_DAY_OFFSET) -> NICInfo:
    nic_type, birth_year, raw_day_code = parse_nic_base(nic)
    if raw_day_code > 500:
        gender = "Female"
        day_code = raw_day_code - 500
    else:
        gender = "Male"
        day_code = raw_day_code
    if day_code < 0 or day_code > 366 + offset + 5:
        raise ValueError("NIC day code out of expected range")
    birth_date = nic_to_date(birth_year, day_code, offset=offset)
    return NICInfo(
        nic_type=nic_type,
        gender=gender,
        birth_year=birth_year,
        raw_day_code=raw_day_code,
        day_code=day_code,
        birth_date=birth_date,
    )

def nic_banner():
    nic_art = [
        "",
        " ███╗   ██╗ ██╗  ██████╗",
        " ████╗  ██║ ██║ ██╔════╝",
        " ██╔██╗ ██║ ██║ ██║     ",
        " ██║╚██╗██║ ██║ ██║     ",
        " ██║ ╚████║ ██║ ╚██████╗",
        " ╚═╝  ╚═══╝ ╚═╝  ╚═════╝"
    ]
    for line in nic_art:
        print(line)
    print("=" * 25)

def main():
    try:
        nic_banner()
        nic = input("\nEnter NIC number: ").strip()
        info = decode_nic(nic)
        print(f"\nNIC Type: {info.nic_type}")
        print(f"Birth Year: {info.birth_year}")
        print(f"Gender: {info.gender}")
        print("Date of Birth:", info.birth_date.strftime("%d %B %Y"),"\n")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
