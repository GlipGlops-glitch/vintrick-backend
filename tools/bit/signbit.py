import sys
import time
import hmac
import hashlib
import base64
import json

api_secret = sys.argv[1]
method = sys.argv[2]
request_path = sys.argv[3]
body = sys.argv[4] if len(sys.argv) > 4 else ''
timestamp = str(int(time.time()))

message = timestamp + method + request_path + body
hmac_key = base64.b64decode(api_secret)
signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
signature_b64 = base64.b64encode(signature.digest()).decode()

result = {
    "CB-ACCESS-SIGN": signature_b64,
    "CB-ACCESS-TIMESTAMP": timestamp
}
print(json.dumps(result))