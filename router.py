from fastapi import APIRouter, UploadFile, HTTPException, Request
from datetime import datetime
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account
import json

from pydantic import BaseModel

router = APIRouter(
   prefix="/projects",
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

@router.post("/notification/")
async def u_money_notification(request: Request):
   body = str(await request.body())
   
   position_label = body.find("amount")
   not_full_label = body[position_label:]
   end_position_label = not_full_label.find("&")
   label = not_full_label
   if end_position_label != -1:
      label = not_full_label[:end_position_label]
   
   print(label)
   return {"status": "OK"}