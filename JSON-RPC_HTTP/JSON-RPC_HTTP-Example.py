# built ins
import sys
import hashlib
import hmac
import time
import requests

# imported from project
sys.path.append('/home/elliotp/dev/deribit/API-Guide/Deribit-API_Authentication-Examples/User-Credentials')                   # noqa: E501
from UserCredentials import Client_Id, Client_Secret                                                                          # noqa: E402 E501

class DeribitExchangeVersion:
    def __init__(self, exchange_version):
        self.exchange_version = exchange_version
        self.main()

    def main(self):
        if self.exchange_version == 'live':
            self.exchange_version = 'https://www.deribit.com'
        elif self.exchange_version == 'testnet':
            self.exchange_version = 'https://www.deribit.com'
        else:
            print('Invalid Exchange Version, please try "live" or "testnet"')

        return self.exchange_version


class UserHTTPEngine:
    def __init__(self, Client_Id, Client_Secret, exchange_version):
        self.client_id = Client_Id
        self.client_secret = Client_Secret
        self.exchange_version = exchange_version
        self.main()

    def main(self):
        
        host = "https://test.deribit.com"
        # #host = "https://www.deribit.com"

        # # replace these values with your client-id/secret
        Client_Id = self.client_id
        Client_Secret = self.client_secret

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

        # #the signature is send in the Authorization header of the HTTPS Request, according to described here https://docs.deribit.com/#authentication

        authorization = "deri-hmac-sha256 id="+Client_Id+",ts="+tstamp+",sig="+sig+",nonce="+nonce
        headers = {"Authorization": authorization}

        print("authorization: " + authorization)
        print("POST request to " + (host+uri+"?"))

        # here we send HTTPS POST request

        json = requests.post((host+uri+"?"), headers=headers, data=body)

        # # te reply is printed
        print(json.content)


if __name__ == "__main__":
    # Your "exchange_version" variable must be 'live' or 'testnet'.
    exchange_version = 'testnet'

    # host = "https://test.deribit.com"
    # #host = "https://www.deribit.com"

    # # replace these values with your client-id/secret
    # Client_Id = Client_Id
    # Client_Secret = Client_Secret

    # tstamp = str(int(time.time())*1000)

    # #nonce must be be a random string from security reasons, here for simplcity
    # nonce = "1234567890"

    # #Does not need ot be the same as the body string dict. The string dict "body" has priority/preference
    # uri = "/api/v2/private/sell"

    # # this is body of the POST request, it is JSON-RPC string, the fields are described here https://docs.deribit.com/#private-buy
    # body = "{\"jsonrpc\": \"2.0\",\"id\": \"6091\",\"method\": \"private/sell\",\"params\": {\"instrument_name\": \"BTC-PERPETUAL\",\"amount\": 20,\"price\": \"10000\",\"label\": \"test_order_1560335086587\"}}"

    # # here we prepare signature for the request, this several lines prepare the hash of the signature
    # request_data = "POST" + "\n" + uri + "\n" + body + "\n"
    # base_signature_string = tstamp + "\n" + nonce + "\n" + request_data
    # byte_key = Client_Secret.encode()
    # message = base_signature_string.encode()
    # sig = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

    # #the signature is send in the Authorization header of the HTTPS Request, according to described here https://docs.deribit.com/#authentication

    # authorization = "deri-hmac-sha256 id="+Client_Id+",ts="+tstamp+",sig="+sig+",nonce="+nonce
    # headers = {"Authorization": authorization}

    UserHTTPEngine(Client_Id=Client_Id,
                   Client_Secret=Client_Secret,
                   exchange_version=DeribitExchangeVersion(exchange_version=exchange_version).exchange_version)

    # print("authorization: " + authorization)
    # print("POST request to " + (host+uri+"?"))

    # # here we send HTTPS POST request

    # json = requests.post((host+uri+"?"), headers=headers, data=body)

    # # te reply is printed
    # print(json.content)