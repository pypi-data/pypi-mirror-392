import jwt
import datetime
from pyboot.commons.utils.utils import date_datetime_cn,l_str

_SECRET= l_str('replace-with-256-bit-secret', 32, '0')


class JWTExpiredError(RuntimeError):...

def create_jwt_token(data:dict|str, ttl_minutes: float = 21600, secret:str=_SECRET, scope:str='read write') -> str:    
    payload = {
        'data':data,
        'exp': date_datetime_cn() + datetime.timedelta(minutes=ttl_minutes),
        'iat': date_datetime_cn(),
        'scope': scope
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def verify_jwt_token(token: str, secret:str=_SECRET) -> dict[str, any]:
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise JWTExpiredError('token已过期')
    except jwt.InvalidTokenError:
        raise JWTExpiredError('token无效')
    except Exception as e:
        raise JWTExpiredError('token错误') from e
    