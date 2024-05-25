from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account
import json
import requests

from pydantic import BaseModel

router = APIRouter(
   tags=["Проекты"],
)

class Notification(BaseModel):
   notification_type: str = None
   operation_id: str = None
   amount: float = None
   withdraw_amount: float = None
   currency: str = None
   datetime: datetime = None
   sender: str = None
   codepro: bool = None
   label: str = None
   sha1_hash: str = None
   test_notification: bool = None
   unaccepted: bool = None

@router.get("/pay/")
async def pay(account: str):
   # Открывает конфиг
   f_config = open("./config.json")
   f_abi_account_contract = open("./contracts/AccountContract.json")

   config = json.load(f_config)
   abi_account_contract = json.load(f_abi_account_contract)

   owner_private_key = config["config"]["blockchain"]["owner_private_key"]
   rpc_server = config["config"]["blockchain"]["rpc_server"]
   account_contract_address = config["config"]["blockchain"]["smart_contracts"]["account_contract"]["address"]

   w3 = Web3(Web3.HTTPProvider(rpc_server))
   owner = Account.from_key(owner_private_key)

   account = Web3.to_checksum_address(account)
   account_contract = w3.eth.contract(address=account_contract_address, abi=abi_account_contract)
   print(account_contract.functions.getAccount(account).call({"from": owner.address}))
   return {"status": "OK"}

@router.get("/pay_page/", response_class=HTMLResponse)
async def pay_page(code: str = None):
   html_content = f"""
    <!DOCTYPE html>
      <html lang="en">
      <head>
         <meta charset="UTF-8" />
         <meta name="viewport" content="width=device-width, initial-scale=1.0" />
         <title>Document</title>
      </head>
      <body>
      {code}
         <form method="POST" action="https://yoomoney.ru/quickpay/confirm">
            <input type="hidden" name="receiver" value="4100118691610961" />
            <input type="hidden" name="label" value="$order_id" />
            <input type="hidden" name="quickpay-form" value="button" />
            <input type="hidden" name="sum" value="10" data-type="number" />
            <label><input type="radio" name="paymentType" value="PC" />ЮMoney</label>
            <label
            ><input type="radio" name="paymentType" value="AC" />Банковской
            картой</label
            >
            <input type="submit" value="Перевести" />
         </form>
      </body>
      <script>

      </script>
      </html>
    """
   return HTMLResponse(content=html_content, status_code=200)

@router.get("/request_pay_page/", response_class=HTMLResponse)
async def request_pay_page(code: str = None):
   response = requests.post("https://yoomoney.ru/oauth/authorize", 
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            data="client_id=37B2979DA7A8F2BA802D236FF49625CBA9BB992A44F3DED85E193E32D86921C3&response_type=code&redirect_uri=http://194.59.40.99:8009/pay_page&scope=account-info operation-history")
   html_content = response.text
   return HTMLResponse(content=html_content, status_code=200)


@router.post("/notification/")
async def u_money_notification(request: Request):
   body = str(await request.body())
   
   label = parse_request(body, "amount")
   
   print(f"{label=}")
   return {"status": "OK"}



def parse_request(full_str: str, label: str) -> str:
   position_label = full_str.find(label)
   not_full_label = full_str[position_label + len(label) + 1:]
   end_position_label = not_full_label.find("&")
   find_str = not_full_label
   if end_position_label != -1:
      find_str = not_full_label[:end_position_label]
   return find_str

