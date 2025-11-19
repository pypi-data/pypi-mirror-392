from datetime import datetime, timedelta, timezone

# 获取当前 UTC 时间
nowTime = datetime.now(timezone.utc)
# 获取当前时间的时间戳
nowTime_timestamp = nowTime.timestamp()
token_exp = nowTime + timedelta(days=30)
token_exp_timestamp = token_exp.timestamp()

print(f"当前时间: {nowTime} (UTC), 时间戳: {nowTime_timestamp}")
print(f"Token 过期时间: {token_exp} (UTC), 时间戳: {token_exp_timestamp}")
