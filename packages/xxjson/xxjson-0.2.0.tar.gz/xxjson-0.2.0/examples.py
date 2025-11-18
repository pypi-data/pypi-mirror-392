import datetime
import xxjson

x = xxjson.dumps({"hello": "world", "key": [1,2,3], "time": "2025-11-14T14:33:30Z", "time2": datetime.datetime(2024, 10, 23, 0, 0, 0)})
print(x)
data = xxjson.loads(x)
print(data)
