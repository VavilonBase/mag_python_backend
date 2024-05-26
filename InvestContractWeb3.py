from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from config import Config


class InvestContractWeb3:
    invest_contract: Contract

    def __init__(self, w3: Web3):
        config = Config()
        self.invest_contract = w3.eth.contract(address=config.invest_contract_address, abi=config.get_invest_abi())

    def assign_get_money(self, project_number: int, author: ChecksumAddress, invest_number: int, amount: int,
                         from_address):
        self.invest_contract.functions.assignGetMoney(project_number, author, invest_number, amount).transact(
            {"from": from_address})
