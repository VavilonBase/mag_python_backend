import requests

from config import Config


class ResponseToken:
    access_token: str
    error: str
    error_msg: str

    def __init__(self, access_token: str, error: str, error_msg: str):
        self.access_token = access_token
        self.error = error
        self.error_msg = error_msg


class ResponseRequestPayment:
    status: str
    error: str
    request_id: str

    def __init__(self, status: str, error: str, request_id: str):
        self.status = status
        self.error = error
        self.request_id = request_id


class ResponseProcessPayment:
    status: str
    error: str
    payment_id: str

    def __init__(self, status: str, error: str, payment_id: str):
        self.status = status
        self.error = error
        self.payment_id = payment_id


class UMoney:
    request_payment_url: str = "https://yoomoney.ru/api/request-payment"
    request_process_url: str = "https://yoomoney.ru/api/process-payment"
    request_authorize_url: str = "https://yoomoney.ru/oauth/authorize"
    request_token_url: str = "https://yoomoney.ru/oauth/token"

    @classmethod
    def request_token(cls, project_number: int, author: str, invest_number: int, code: str = None) -> ResponseToken:
        config = Config()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"code": code, "client_id": config.client_id,
                "redirect_uri": f"{config.host}:{config.port}/pay_page/?project_number={project_number}&author={author}&invest_number={invest_number}",
                "grant_type": "authorization_code"}

        response = requests.post(cls.request_token_url,
                                 headers=headers,
                                 data=data)
        response_data = response.json()

        # Если есть ошибки
        if "error" in response_data:
            error_msg = ""
            if response_data["error"] == "invalid_request":
                error_msg = "Обязательные параметры запроса отсутствуют или имеют некорректные или недопустимые значения."
            elif response_data["error"] == "unauthorized_client":
                error_msg = "Неверное значение параметра client_id или client_secret, либо приложение не имеет права запрашивать авторизацию (например, ЮMoney заблокировали его client_id)."
            else:
                error_msg = "В выдаче access_token отказано. ЮMoney не выдавали временный токен, токен просрочен, или по этому временному токену уже выдан access_token (повторный запрос токена авторизации с тем же временным токеном)."
            return ResponseToken("", response_data["error"], error_msg)
        return ResponseToken(response_data["access_token"], "", "")

    @classmethod
    def request_authorize(cls, project_number: int, author: str, invest_number: int) -> str:
        config = Config()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": config.client_id,
            "redirect_uri": f"{config.host}:{config.port}/pay_page/?project_number={project_number}&author={author}&invest_number={invest_number}",
            "scope": "payment-p2p account-info operation-history"
        }
        print(data["redirect_uri"])
        response = requests.post(cls.request_authorize_url,
                                 headers=headers,
                                 data=data)
        html_content: str = response.text
        return html_content

    @classmethod
    def request_payment(cls, to: str, amount_due: str, message: str, label: str,
                        access_token: str) -> ResponseRequestPayment:
        data = {
            "pattern_id": "p2p",
            "to": to,
            "amount_due": amount_due,
            "message": message,
            "label": label
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + str(access_token)
        }

        response = requests.post(cls.request_payment_url,
                                 headers=headers,
                                 data=data)

        response_data = response.json()
        status: str = response_data["status"]

        if status == "success":
            return ResponseRequestPayment(status, "", response_data["request_id"])
        else:
            return ResponseRequestPayment(status, response_data["error"], "")

    @classmethod
    def process_payment(cls, request_id: str, access_token: str) -> ResponseProcessPayment:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + str(access_token)
        }

        data = {
            "request_id": request_id
        }

        response = requests.post(cls.request_process_url,
                                 headers=headers,
                                 data=data)

        response_data = response.json()
        status: str = response_data["status"]

        if status == "success":
            return ResponseProcessPayment(status, "", response_data["payment_id"])
        elif status == "refused":
            return ResponseProcessPayment(status, response_data["error"], "")
        else:
            return ResponseProcessPayment(status, "Повторите попытку позднее", "")
