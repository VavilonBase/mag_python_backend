from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from web3 import Web3

from InvestContractWeb3 import InvestContractWeb3
from ParseRequest import ParseRequest
from UMoney import UMoney, ResponseRequestPayment, ResponseProcessPayment, ResponseToken
from config import Config

router = APIRouter()


@router.post("/pay/")
async def pay(request: Request):
    # Получаем параметры запроса
    body = str(await request.body()).strip("'")
    params = ParseRequest.parse_request(body, "receiver", "access_token", "amount", "project_number", "author",
                                        "invest_number")
    message = f"{params['project_number']},{params['author']},{params['invest_number']}"

    # Отправялем запрос на оплату
    response_request_payment: ResponseRequestPayment = UMoney.request_payment(params["receiver"], params["amount"],
                                                                              message, message, params["access_token"])

    # Если запрос на оплату завершился ошибкой
    if response_request_payment.status != "success":
        return {"status": response_request_payment.status, "message": "", "error": response_request_payment.error}

    # Подтверждаем оплату
    response_process_payment: ResponseProcessPayment = UMoney.process_payment(response_request_payment.request_id,
                                                                              params["access_token"])
    # Если подтверждение оплаты завершилось ошибкой
    if response_process_payment.status != "success":
        return {"status": response_process_payment.status, "error": response_process_payment.error}

    # Если оплата успешно прошла
    return {"status": "success", "message": "Оплата успешно произведена", "error": ""}


@router.get("/pay_page/", response_class=HTMLResponse)
async def pay_page(project_number: int, author: str, invest_number: int, code: str = None):
    config = Config()
    response_token: ResponseToken = UMoney.request_token(project_number, author, invest_number, code)

    html_content = ""

    if response_token.error != "":
        print(response_token.error_msg)
        html_content = f'''
          <!DOCTYPE html>
          <html lang="en">
          <head>
             <meta charset="UTF-8" />
             <meta name="viewport" content="width=device-width, initial-scale=1.0" />
             <title>Техническая ошибка</title>
          </head>
          <body>
             Произошла техническая ошибка
          </body>
          </html>
          '''
    else:
        html_content = f'''
              <!DOCTYPE html>
              <html lang="en">
              <head>
                 <meta charset="UTF-8" />
                 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                 <title>Document</title>
              </head>
              <body>
                 <form method="POST" action="{config.host}:{config.port}/pay">
                    <input type="hidden" name="receiver" value="4100118691610961" /><br/>
                    <input type="hidden" value={project_number} name="project_number" /><br/>
                    <input type="hidden" value={author} name="author" /><br/>
                    <input type="hidden" value={invest_number} name="invest_number" /><br/>
                    <input type="hidden" name="access_token" value={response_token.access_token} /><br/>
                    Введите сумму: <input name="amount" /> руб.<br/>
                    <input type="submit" value="Перевести" />
                 </form>
              </body>
              </html>
              '''

    return HTMLResponse(content=html_content, status_code=200)


@router.get("/request_authorize/", response_class=HTMLResponse)
async def request_authorize(project_number: int, author: str, invest_number: int):
    return HTMLResponse(content=UMoney.request_authorize(project_number, author, invest_number), status_code=200)


@router.post("/notification/")
async def u_money_notification(request: Request):
    config = Config()

    # Получаем параметры
    body = str(await request.body())
    params: dict = ParseRequest.parse_request(body, "amount", "label")
    amount: int = int(params["amount"].replace(".", ""))  # Сумма перевода
    labels: list[str] = params["label"].split("%2C")  # Метки
    project_number: int = int(labels[0])  # Номер проекта
    author: ChecksumAddress = Web3.to_checksum_address(labels[1])  # Автор проекта
    invest_number: int = int(labels[2])  # Номер инвестиции

    w3: Web3 = Web3(Web3.HTTPProvider(config.rpc_server))
    owner: LocalAccount = Account.from_key(config.owner_private_key)

    invest_contract = InvestContractWeb3(w3)

    invest_contract.assign_get_money(project_number, author, invest_number, amount, owner.address)
    return {"status": "OK"}
