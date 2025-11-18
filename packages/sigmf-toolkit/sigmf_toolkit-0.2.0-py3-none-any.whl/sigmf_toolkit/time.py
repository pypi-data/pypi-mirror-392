import datetime


def parse_datetime(dt):
    if dt[-1] == "Z":
        dt = dt[:-1]
    if "." not in dt:
        integer = dt
        frac = 0.0
    else:
        integer, frac = dt.split(".")
        frac = float(f"0.{frac}")
    try:
        unix_timestamp = int(integer)
        timestamp = datetime.datetime.fromtimestamp(
            unix_timestamp, datetime.timezone.utc
        ).replace(tzinfo=None)
    except ValueError:
        timestamp = datetime.datetime.fromisoformat(integer)
        assert timestamp.tzinfo is None
    return f"{timestamp.isoformat()}.{str(frac).split('.')[1]}Z"
