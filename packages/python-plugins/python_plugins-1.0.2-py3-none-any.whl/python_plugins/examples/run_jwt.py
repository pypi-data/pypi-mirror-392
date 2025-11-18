import time
import datetime
import jwt


def jwt_encode(payload: dict, key: str, delta: int = None, algorithm="HS256"):
    """encode payload.

    :param payload: _description_
    :param key: _description_
    :param delta: _description_, defaults to None
    :param algorithm: _description_, defaults to "HS256"
    :return: An encoded access token
    """
    if delta and delta > 0:
        exp = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=delta
        )
        payload |= {"exp": exp}

    token = jwt.encode(payload, key, algorithm)
    return token


def jwt_decode(encoded, key: str, algorithm="HS256"):
    """decode jwt."""

    payload = jwt.decode(encoded, key, algorithm)
    return payload


def run_jwt(fake):
    payload = {"some": fake.sentence()}
    key = fake.vin()
    # print(payload, key)
    token = jwt_encode(payload, key)
    # print(token)
    decoded = jwt_decode(token, key)
    # print(decoded)
    assert decoded["some"] == payload["some"]
    delta = 100
    token = jwt_encode(payload, key, delta)
    # print(token)
    decoded = jwt_decode(token, key)
    # print(decoded)
    assert decoded["some"] == payload["some"]
    # print(decoded["exp"],time.mktime(datetime.datetime.now().timetuple()))
    assert "exp" in decoded
    exp_time = time.mktime(datetime.datetime.now().timetuple()) + delta - 10
    assert decoded["exp"] > exp_time
    # print(datetime.datetime.fromtimestamp(decoded["exp"]))
