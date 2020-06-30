# JSON-RPC over HTTPS Example
# A reason to use JSON-RPC over HTTPS is to avoid the sole use of your Client ID and Client Secret

#Built-Ins
import hashlib
import hmac
import time
import requests

# Package Variables
from UserCredentials import Client_Id, Client_Secret

# IMPORTANT: www.deribit.com and test.deribit.com do not share Account Credentials or API Keys.
# You must activate an API key in your Account Settings to create a "Client Id" and a "Client Signature"

host = "https://test.deribit.com"
#host = "https://www.deribit.com"

# replace these values with your client-id/secret
Client_Id = Client_Id
Client_Secret = Client_Secret

tstamp = str(int(time.time())*1000)

#nonce must be be a random string from security reasons, here for simplcity
nonce = "1234567890"

#Does not need ot be the same as the body string dict. The string dict "body" has priority/preference
uri = "/api/v2/private/sell"

# this is body of the POST request, it is JSON-RPC string, the fields are described here https://docs.deribit.com/#private-buy
body = "{\"jsonrpc\": \"2.0\",\"id\": \"6091\",\"method\": \"private/sell\",\"params\": {\"instrument_name\": \"BTC-PERPETUAL\",\"amount\": 20,\"price\": \"10000\",\"label\": \"test_order_1560335086587\"}}"

# here we prepare signature for the request, this several lines prepare the hash of the signature
request_data = "POST" + "\n" + uri + "\n" + body + "\n"
base_signature_string = tstamp + "\n" + nonce + "\n" + request_data
byte_key = Client_Secret.encode()
message = base_signature_string.encode()
sig = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

#the signature is send in the Authorization header of the HTTPS Request, according to described here https://docs.deribit.com/#authentication

authorization = "deri-hmac-sha256 id="+Client_Id+",ts="+tstamp+",sig="+sig+",nonce="+nonce
headers = {"Authorization": authorization}

print("authorization: " + authorization)
print("POST request to " + (host+uri+"?"))

# here we send HTTPS POST request

json = requests.post((host+uri+"?"), headers=headers, data=body)

# te reply is printed
print(json.content)



