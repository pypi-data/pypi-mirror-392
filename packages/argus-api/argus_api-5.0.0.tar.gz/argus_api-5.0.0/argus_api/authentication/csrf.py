from typing import Union
from base64 import b64encode, b64decode
from datetime import datetime
import hmac
import hashlib
import json


def base64urlencode(value: Union[str, bytes]) -> str:
    """Encode a string to URL-safe base64 (as used by JWT) without padding.

    This implements the "base64url" encoding as described in RFC 4648, section 5.

    :param value: string or bytes to encode
    :return: encoded string
    """
    if isinstance(value, str):
        value = value.encode()
    return (
        b64encode(value).decode().replace("+", "-").replace("/", "_").replace("=", "")
    )


def get_CSRF_token(url: str, session_key: str) -> str:
    """get an Argus CSRF token for the given URL.

    :param url: URL to get a token for
    :param session_key: Argus session (base64-encoded, as given by argus)

    :return: valid CSRF token for the URL
    """
    # RFC 7519: JSON Web Token (JWT) specifies a "typ" field, but argus uses "type"
    jwt_header = {"alg": "HS256", "type": "JWT"}
    jwt_header_encoded = base64urlencode(json.dumps(jwt_header))

    now = datetime.now()
    timestamp = int(now.timestamp() * 1000)
    jwt_payload = {"url": url, "timestamp": timestamp}
    jwt_payload_encoded = base64urlencode(json.dumps(jwt_payload))

    jwt_data = f"{jwt_header_encoded}.{jwt_payload_encoded}"

    decoded_key = b64decode(session_key)

    hs256 = hmac.new(
        decoded_key,
        jwt_data.encode(),
        hashlib.sha256,
    )
    signature = base64urlencode(hs256.digest())

    token = f"{jwt_data}.{signature}"
    return token
