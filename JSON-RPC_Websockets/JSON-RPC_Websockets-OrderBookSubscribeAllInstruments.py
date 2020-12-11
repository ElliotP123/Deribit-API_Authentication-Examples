# built ins
import time
from datetime import datetime, timedelta
import hashlib
import hmac
import json
import secrets

# installed
import websocket

class DeribitAPIAccessScope:
    def __init__(self, scope):
        self.scope = scope
        self.main()

    def main(self):
        if self.scope == 'read-only':
            self.account_scope = "read"
            self.trade_scope = "read"
            self.wallet_scope = "read"
            self.block_scope = "read"
            self.custody = "read_write"  # Must be 'read_write' for the moment given the present API implementation           # noqa: E501
            self.designated_scope = "account:{} trade:{} wallet:{} block_trade:{} custody:{}".format(
                                                                                                        self.account_scope,   # noqa: E501
                                                                                                        self.trade_scope,     # noqa: E501
                                                                                                        self.wallet_scope,    # noqa: E501
                                                                                                        self.block_scope,     # noqa: E501
                                                                                                        self.custody          # noqa: E501
                                                                                                    )                         # noqa: E501
            print('Scope Definition: You are using "{}" access'.format(self.scope))                                           # noqa: E501
        elif self.scope == 'read-write':
            self.account_scope = "read_write"
            self.trade_scope = "read_write"
            self.wallet_scope = "read_write"
            self.block_scope = "read_write"
            self.custody = "read_write"
            self.designated_scope = "account:{} trade:{} wallet:{} block_trade:{} custody:{}".format(                         # noqa: E501
                                                                                                        self.account_scope,   # noqa: E501
                                                                                                        self.trade_scope,     # noqa: E501
                                                                                                        self.wallet_scope,    # noqa: E501
                                                                                                        self.block_scope,     # noqa: E501
                                                                                                        self.custody          # noqa: E501
                                                                                                    )                         # noqa: E501
            print('Scope Definition: You are using "{}" access'.format(self.scope))                                           # noqa: E501
        else:
            self.designated_scope = self.scope
            print('Invalid Scope Definition: "{}" is not an accepted scope definition. Please try "read-only" or "read-write".'.format(self.scope))  # noqa: E501
            print('You will receive inconsistent scope definitions.')

        return self.designated_scope


class DeribitExchangeVersion:
    def __init__(self, exchange_version):
        self.exchange_version = exchange_version
        self.main()

    def main(self):
        if self.exchange_version == 'live':
            self.exchange_version = 'wss://www.deribit.com/ws/api/v2/'
        elif self.exchange_version == 'testnet':
            self.exchange_version = 'wss://test.deribit.com/ws/api/v2/'
        else:
            print('Invalid Exchange Version, please try "live" or "testnet"')

        return self.exchange_version


class UserWebsocketEngine:
    def __init__(self, client_Id, scope, exchange_version):
        self.client_id = client_Id
        self.scope = scope
        self.exchange_version = exchange_version
        self.expiry_time = None
        self.refresh_token = ''
        self.authentication_refresh_flag = 0
        self.heartbeat_requested_flag = 0
        self.heartbeat_set_flag = 0
        self.instruments_list = []
        self.pulled_instruments_flag = 0
        self.pulled_instruments_datetime = datetime.utcnow() + timedelta(hours=12)
        self.instruments_subscribe_flag = 0
        self.main()

    def main(self):
        def on_message(ws, message):
            message = json.loads(message)
            # print("Message Received at: " + str(datetime.now().time().strftime('%H:%M:%S')))                                # noqa: E501
            # print(message)
            # print(message.keys())

            if 'error' in message.keys():
                error_message = message['error']['message']
                error_code = message['error']['code']
                print('You have received an ERROR MESSAGE: {} with the ERROR CODE: {}'.format(error_message, error_code))     # noqa: E501

            # display successful authentication messages as well as stores your refresh_token                                 # noqa: E501
            if 'result' in message.keys():
                if [*message['result']] == ['token_type', 'scope', 'refresh_token', 'expires_in', 'access_token']:            # noqa: E501
                    if self.authentication_refresh_flag == 1:
                        print('Successfully Refreshed your Authentication at: ' +
                            str(datetime.now().time().strftime('%H:%M:%S')))
                    else:
                        print('Authentication Success at: ' + str(datetime.now().time().strftime('%H:%M:%S')))                # noqa: E501
                    self.refresh_token = message['result']['refresh_token']
                    if message['testnet']:
                        # The testnet returns an extremely high value for expires_in and is best to use                       # noqa: E501
                        # 600 in place as so the functionality is as similar as the Live exchange                             # noqa: E501
                        expires_in = 600
                    else:
                        expires_in = message['result']['expires_in']

                    self.expiry_time = (datetime.now() + timedelta(seconds=expires_in))                                       # noqa: E501
                    print('Authentication Expires at: ' + str(self.expiry_time.strftime('%H:%M:%S')))                         # noqa: E501

            # uses your refresh_token to refresh your authentication
            if datetime.now() > self.expiry_time and self.authentication_refresh_flag == 0:                                   # noqa: E501
                self.authentication_refresh_flag = 1
                print('Refreshing your Authentication at: ' + str(self.expiry_time.strftime('%H:%M:%S')))                     # noqa: E501
                ws_data = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "public/auth",
                    "params": {
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token
                    }
                }
                ws.send(json.dumps(ws_data))

            # heartbeat set success check and heartbeat response
            if 'params' in message.keys() and message['params']['type'] == 'heartbeat' and self.heartbeat_set_flag == 0:      # noqa: E501
                self.heartbeat_set_flag = 1
                print('Heartbeat Successfully Initiated at: ' + str(datetime.now().time().strftime('%H:%M:%S')))              # noqa: E501

            # respond to a test request
            if 'params' in message.keys() and message['params']['type'] == 'test_request':                                    # noqa: E501
                ws_data = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "public/test",
                    "params": {
                    }
                }
                ws.send(json.dumps(ws_data))

            # print of successful order book subscription
            if message['id'] == 42:
                print('Successfully Subscribed to Order Book Data at: {}'.format(datetime.utcnow()))
                for channel in range(0, len(message['result'])):
                    message_split = message['result'][channel].split('.')
                    # print('Subscription Channel: {}'.format(message_split[1]))
                    # print('Price Groupings: {}'.format(message_split[2]))
                    # print('Price Levels/Depth: {}'.format(message_split[3]))
                    # print('Interval: {}'.format(message_split[4]))

            # construct channels to subscribe to from pull instruments
            if message['id'] == 7617:
                self.pulled_instruments_flag = 1
                for instrument in range(0,len(message['result'])):
                    subscribe_channel = "book."+str(message['result'][instrument]['instrument_name'])+".none.10.100ms"
                    self.instruments_list.append(subscribe_channel)

            # subscribe to all available instruments
            if self.instruments_subscribe_flag == 0 and self.pulled_instruments_flag == 1:
                # Subscribing to the Order Book
                ws_data = {"jsonrpc": "2.0",
                            "method": "public/subscribe",
                            "id": 42,
                            "params": {
                                "channels": self.instruments_list
                                        }
                            }
                ws.send(json.dumps(ws_data))

                self.instruments_subscribe_flag = 1

            # repull all instruments and resubscribe
            if datetime.utcnow() > self.pulled_instruments_datetime:
                self.pulled_instruments_flag = 0
                self.instruments_subscribe_flag = 0
                self.instruments_list = []

                # incrementing the /get_instruments datetime
                self.pulled_instruments_datetime = datetime.utcnow() + timedelta(hours=12)

                # Sending the request
                ws_data ={
                    "jsonrpc": "2.0",
                    "id": 7617,
                    "method": "public/get_instruments",
                    "params": {
                        "currency": "BTC",
                        "kind": "option",
                        "expired": False
                                }
                    }
                ws.send(json.dumps(ws_data))



        def on_error(ws, error):
            if type(error == "<class 'websocket._exceptions.WebSocketBadStatusException'>"):  # noqa: E501
                print('')
                print('ERROR MESSAGE:'+'Testnet is likely down for maintenance or your connection is unstable unless you cancelled this yourself.')  # noqa: E501
                print('')
            else:
                print(error)

        def on_close(ws):
            print('CONNECTION CLOSED AT: ' + str(datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501

        def on_open(ws):
            # Initial Authentication
            ws_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "public/auth",
                "params": {
                    "grant_type": "client_signature",
                    "client_id": self.client_id,
                    "timestamp": tstamp,
                    "nonce": nonce,
                    "scope": self.scope,
                    "signature": signature,
                    "data": data}
            }
            ws.send(json.dumps(ws_data))

            # Initiating Heartbeat
            if self.heartbeat_set_flag == 0 and self.heartbeat_requested_flag == 0:                                                     # noqa: E501
                self.heartbeat_requested_flag = 1
                print('Heartbeat Requested at: ' + str(datetime.now().time().strftime('%H:%M:%S')))                                     # noqa: E501
                ws_data = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "public/set_heartbeat",
                            "params": {
                                "interval": 10
                            }
                            }
                ws.send(json.dumps(ws_data))

            # Pull all available BTC Option Instrument Names
            ws_data ={
                    "jsonrpc": "2.0",
                    "id": 7617,
                    "method": "public/get_instruments",
                    "params": {
                        "currency": "BTC",
                        "kind": "option",
                        "expired": False
                                }
                    }
            ws.send(json.dumps(ws_data))

        # Detailed Logging
        # websocket.enableTrace(True)

        # Initialize Websocket App
        ws = websocket.WebSocketApp(self.exchange_version,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open

        ws.run_forever()


if __name__ == "__main__":
    # Local Testing
    Client_Id = "XBagIoFw"
    Client_Secret = "BtsbXxYRbpct7ZB44BEidFPlhICBoDAOQadZ31QD_mY"
    Client_Id = "Ac5nOoVh"
    Client_Secret = "hrOkDCReLk00b70fBgZHolzbakzF5iGg7I4_E9hlYIc"
    
    # Your "scope" variable must be 'read-only' or 'read-write'.
    scope = 'read-only'
    # Your "exchange_version" variable must be 'live' or 'testnet'.
    exchange_version = 'testnet'

    # Client Signature Authentication
    tstamp = str(int(time.time()) * 1000)
    data = ''
    nonce = secrets.token_urlsafe(10)
    base_signature_string = tstamp + "\n" + nonce + "\n" + data
    byte_key = Client_Secret.encode()
    message = base_signature_string.encode()
    signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

    # Your Trading Engine
    UserWebsocketEngine(client_Id=Client_Id,
                        scope=DeribitAPIAccessScope(scope).designated_scope,
                        exchange_version=DeribitExchangeVersion(exchange_version).exchange_version)                           # noqa: E501
