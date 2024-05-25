from fastapi import APIRouter, UploadFile, HTTPException
from schemas import SProject, SProjectAdd, SProjectId, SProjectFullAdd
from repository import ProjectRepository
import datetime
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account
import json

router = APIRouter(
   prefix="/projects",
   tags=["Проекты"],
)

@router.get("/")
async def get_projects() -> list[SProject]:
   projects = await ProjectRepository.get_projects()
   return projects

@router.get("/project/")
async def get_project(author: str, projectNumber: int) -> SProject:
   project = await ProjectRepository.get_project(projectNumber, author)
   if project is None:
      raise HTTPException(status_code=404, detail="Проект не найден")
   return project

@router.post("/")
async def add_project(project: SProjectAdd) -> SProjectId:
   add_project: SProjectFullAdd = SProjectFullAdd(number=project.number, author=project.author, description=project.description,
                                                  dt_from=datetime.date.today(), dt_to=datetime.date.today() + datetime.timedelta(days=14))
   new_project_id = await ProjectRepository.add_project(add_project)
   return {"id": new_project_id}

@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    data = await file.read()
    filename = str(datetime.datetime.timestamp(datetime.datetime.now())) + file.filename
    save_to = "static/" + filename
    with open(save_to, "wb") as f:
       f.write(data)
    return {"success": 1, "file": {"url": f"http://localhost:8000/{save_to}"} }

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

@router.get("/notification/")
async def u_money_notification(request):
   print(request.body)
   return {"status": "OK"}