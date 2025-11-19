# -*- coding:utf-8 -*-
import jwt
import pytz
import logging
from typing import Optional
from datetime import datetime, timedelta, timezone


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PassportService:

    def __init__(self, sk: Optional[str] = None):
        if sk:
            self.sk = sk
        else:
            self.sk = "WuZ6knpkFXpHxEQD+lrZzRXHz4m63udb/eOJhWJgXXjmr+Fq139EX3Es"

    def issue(self, payload):
        if not payload:
            return None
        return jwt.encode(payload, self.sk, algorithm="HS256")

    def verify(self, token):
        try:
            return jwt.decode(token, self.sk, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            logger.error("Invalid token signature.")
        except jwt.exceptions.ExpiredSignatureError:
            logger.error("Token has expired.")
        except jwt.exceptions.InvalidTokenError:
            logger.error("Invalid token.")
        except Exception:
            logger.error("Verify token exception.")


def test_timestamp_conversion(timestamp: int, tz=timezone.utc) -> datetime:
    """
    测试将Unix时间戳转换为指定时区的本地时间。

    参数:
        timestamp (int): Unix时间戳。
        tz (datetime.timezone, optional): 目标时区，默认为UTC。
    """
    try:
        # 根据给定的时间戳和时区创建UTC时间的datetime对象
        utc_time = datetime.fromtimestamp(timestamp, tz=tz)
        # 转换为目标时区的本地时间
        shanghai_tz = pytz.timezone("Asia/Shanghai")
        local_time = utc_time.astimezone(shanghai_tz)
        return local_time
    except (ValueError, OverflowError) as e:
        # 处理无效或溢出的时间戳情况
        raise ValueError(f"无效的时间戳: {timestamp}") from e


if __name__ == "__main__":
    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDViOTg2NzQtYzdkOS00NDIyLTgwYWUtNTQxMGJiZDg1NGQyIiwiYXBwX2lkIjoiZGJjODg4NWE1NDdmNjMwYyIsImFwaV9zZWNyZXQiOiIzODBhMjhiZmU5N2Q1NGVjN2UwMGJkNzlhYTU5ZjY2NyIsImFwaV9rZXkiOiJiNjk5MDBiZTczMmIxYmRiOWU5ZjM3NTY1N2FmMWY2ZiIsImlhdCI6MTc1NTY3MTI0NiwiZ3JhbnRfdHlwZSI6ImFjY2VzcyIsImV4cCI6MTc1NTY3MzA0NiwiaXNzIjoiU0VMRl9IT1NURUQiLCJzdWIiOiJBUEkgUGFzc3BvcnQgVjEuMCIsImV4dHJhIjoie30ifQ.i6_iehpbt9wu8tixXA0XsM5GfJH69H-o-unUZBeeUQQ"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiM2MzMWFmZDMtYTk0MS00M2ZmLWFiZWYtNjI0YmMxMGM1MDNmIiwiYXBwX2lkIjoiYWY3ZGNjNzdkMTFhMDY4MyIsImFwaV9zZWNyZXQiOiJlNDIwMjEzNmZlN2VhNTU0NjVmOTYwNDg4M2RkZTA1NCIsImFwaV9rZXkiOiJhYjlkNTA2MjRiZTBjYTNkNTdmODhlMDM1YWRiZmQ5NCIsImlhdCI6MTc2MzEwMzg4MiwiZ3JhbnRfdHlwZSI6ImFjY2VzcyIsImV4cCI6MTc2ODUwMzg4MiwiaXNzIjoiU0VMRl9IT1NURUQiLCJzdWIiOiJBUEkgUGFzc3BvcnQgVjEuMCIsImV4dHJhIjoie30ifQ.uLcoHsaNYn16uzBHM8hbcFyZX4D2cOs5ewPm591WuCw"
    payload = PassportService().verify(token)
    print(payload)

    if payload:

        iat = test_timestamp_conversion(payload.get("iat", 0))
        print(f"iat: {iat} (Asia/Shanghai)")

        exp = test_timestamp_conversion(payload.get("exp", 0))
        print(f"exp: {exp} (Asia/Shanghai)")

    utc_time = datetime.fromtimestamp(1747200000000 / 1000, tz=timezone.utc)
    print(f"UTC Time: {utc_time}")
