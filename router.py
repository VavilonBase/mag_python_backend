from fastapi import APIRouter, Request, Body
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

@router.post("/pay/")
async def pay(data =Body()):
   print(data)
   # Открывает конфиг
   # f_config = open("./config.json")
   # f_abi_account_contract = open("./contracts/AccountContract.json")

   # config = json.load(f_config)
   # abi_account_contract = json.load(f_abi_account_contract)

   # owner_private_key = config["config"]["blockchain"]["owner_private_key"]
   # rpc_server = config["config"]["blockchain"]["rpc_server"]
   # account_contract_address = config["config"]["blockchain"]["smart_contracts"]["account_contract"]["address"]

   # w3 = Web3(Web3.HTTPProvider(rpc_server))
   # owner = Account.from_key(owner_private_key)

   # account = Web3.to_checksum_address(account)
   # account_contract = w3.eth.contract(address=account_contract_address, abi=abi_account_contract)
   # print(account_contract.functions.getAccount(account).call({"from": owner.address}))
   return {"status": "OK"}

@router.get("/pay_page/", response_class=HTMLResponse)
async def pay_page(code: str = None):
   client_id="37B2979DA7A8F2BA802D236FF49625CBA9BB992A44F3DED85E193E32D86921C3" # TODO
   grant_type = "authorization_code"
   redirect_uri = "http://194.59.40.99:8009/pay_page"
   headers= {
      "Content-Type": "application/x-www-form-urlencoded"
   }
   response = requests.post("https://yoomoney.ru/oauth/token", 
                            headers=headers,
                            data=f"code={code}&client_id={client_id}&grant_type{grant_type}=&redirect_uri={redirect_uri}")
   access_token=response.text

   html_content = f'''
      <!DOCTYPE html>
      <html lang="en">
      <head>
         <meta charset="UTF-8" />
         <meta name="viewport" content="width=device-width, initial-scale=1.0" />
         <title>Document</title>
      </head>
      <body>
         <form method="POST" action="http://194.59.40.99:8009/pay">
            <input type="hidden" name="receiver" value="4100118691610961" />
            <input type="hidden" name="access_token" value={access_token} />
            <input name="sum" data-type="number" />
            <input type="submit" value="Перевести" />
         </form>
      </body>
      </html>
      '''
   
   return HTMLResponse(content=html_content, status_code=200)



@router.get("/request_pay_page/", response_class=HTMLResponse)
async def request_pay_page(code: str = None):
   client_id = "37B2979DA7A8F2BA802D236FF49625CBA9BB992A44F3DED85E193E32D86921C3"
   redirect_uri = "http://194.59.40.99:8009/pay_page"
   headers= {
      "Content-Type": "application/x-www-form-urlencoded"
   }
   scope="payment-p2p account-info operation-history"
   response = requests.post("https://yoomoney.ru/oauth/authorize", 
                            headers=headers,
                            data=f"client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}")
   html_content = response.text
   return HTMLResponse(content=html_content, status_code=200)


@router.post("/notification/")
async def u_money_notification(request: Request):
   body = str(await request.body())
   
   amount = parse_request(body, "amount")
   label = parse_request(body, "label")
   print(amount)
   print(label)
   return {"status": "OK"}



def parse_request(full_str: str, label: str) -> str:
   position_label = full_str.find(label)
   not_full_label = full_str[position_label + len(label) + 1:]
   end_position_label = not_full_label.find("&")
   find_str = not_full_label
   if end_position_label != -1:
      find_str = not_full_label[:end_position_label]
   return find_str

