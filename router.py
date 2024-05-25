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
async def pay(data = Body()):
   body = data.decode().strip("'")
   
   receiver = parse_request(body, "receiver")
   access_token = parse_request(body, "access_token")
   summ = parse_request(body, "sum")
   project_number = parse_request(body, "project_number")
   author = parse_request(body, "author")
   invest_number = parse_request(body, "invest_number")
   message = f"{project_number},{author},{invest_number},{summ}"
   print(message)
   data = {
      "pattern_id": "p2p",
      "to": receiver,
      "amount_due": summ,
      "message": message,
      "label": message
   }
   
   headers= {
      "Content-Type": "application/x-www-form-urlencoded",
      "Authorization": "Bearer " + str(access_token)
   }
   response = requests.post("https://yoomoney.ru/api/request-payment", 
                            headers=headers,
                            data=data)
   response_data = response.json()
   request_id = response_data["request_id"]

   data = {
      "request_id": request_id
   }

   response = requests.post("https://yoomoney.ru/api/process-payment", 
                            headers=headers,
                            data=data)
   
   response_data = response.json()
   status = response_data["status"]

   return {"status": status}

@router.get("/pay_page/", response_class=HTMLResponse)
async def pay_page(project_number: int, author: str, invest_number: int, code: str = None):
   headers= {
      "Content-Type": "application/x-www-form-urlencoded"
   }
   data={
      "code": code,
      "client_id": "37B2979DA7A8F2BA802D236FF49625CBA9BB992A44F3DED85E193E32D86921C3",
      "redirect_uri": f"http://194.59.40.99:8010/pay_page?project_number={project_number}&author={author}&invest_number={invest_number}",
      "grant_type": "authorization_code"
   }
   response = requests.post("https://yoomoney.ru/oauth/token", 
                            headers=headers,
                            data=data)
   response_data = response.json()
   access_token = response_data["access_token"]

   html_content = f'''
      <!DOCTYPE html>
      <html lang="en">
      <head>
         <meta charset="UTF-8" />
         <meta name="viewport" content="width=device-width, initial-scale=1.0" />
         <title>Document</title>
      </head>
      <body>
         <form method="POST" action="http://194.59.40.99:8010/pay">
            <input type="hidden" name="receiver" value="4100118691610961" /><br/>
            <input type="hidden" value={project_number} name="project_number" /><br/>
            <input type="hidden" value={author} name="author" /><br/>
            <input type="hidden" value={invest_number} name="invest_number" /><br/>
            <input type="hidden" name="access_token" value={access_token} /><br/>
            Введите сумму: <input name="sum" /> руб.<br/>
            <input type="submit" value="Перевести" />
         </form>
      </body>
      </html>
      '''
   
   return HTMLResponse(content=html_content, status_code=200)



@router.get("/request_pay_page/", response_class=HTMLResponse)
async def request_pay_page(project_number: int, author: str, invest_number: int):
   headers= {
      "Content-Type": "application/x-www-form-urlencoded"
   }
   data={
      "client_id": "37B2979DA7A8F2BA802D236FF49625CBA9BB992A44F3DED85E193E32D86921C3",
      "redirect_uri": f"http://194.59.40.99:8010/pay_page?project_number={project_number}&author={author}&invest_number={invest_number}",
      "scope": "payment-p2p account-info operation-history"
   }
   response = requests.post("https://yoomoney.ru/oauth/authorize", 
                            headers=headers,
                            data=data)
   html_content = response.text
   return HTMLResponse(content=html_content, status_code=200)


@router.post("/notification/")
async def u_money_notification(request: Request):
   body = str(await request.body())
   print(body)
   amount = parse_request(body, "amount")
   message = parse_request(body, "label")
   params = message.split(",")
   print(params)
   print(message)
   project_number = params[0]
   author = Web3.to_checksum_address(params[1])
   invest_number = params[2]
   summ = int(params[3].replace(".", ""))

   #Открываем конфиг
   f_config = open("./config.json")
   f_abi_invest_contract = open("./contracts/InvestContract.json")

   config = json.load(f_config)
   abi_invest_contract = json.load(f_abi_invest_contract)

   owner_private_key = config["config"]["blockchain"]["owner_private_key"]
   rpc_server = config["config"]["blockchain"]["rpc_server"]
   invest_contract_address = config["config"]["blockchain"]["smart_contracts"]["invest_contract"]["address"]

   w3 = Web3(Web3.HTTPProvider(rpc_server))
   owner = Account.from_key(owner_private_key)
   
   invest_contract = w3.eth.contract(address=invest_contract_address, abi=abi_invest_contract)
   invest_contract.functions.assignGetMoney(project_number, author, invest_number, summ).transact({"from": owner.address})
   return {"status": "OK"}



def parse_request(full_str: str, label: str) -> str:
   position_label = full_str.find(label)
   not_full_label = full_str[position_label + len(label) + 1:]
   end_position_label = not_full_label.find("&")
   find_str = not_full_label
   if end_position_label != -1:
      find_str = not_full_label[:end_position_label]
   return find_str

