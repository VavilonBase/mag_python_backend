import json
from typing import IO

from eth_typing import ChecksumAddress
from web3 import Web3


class Config:
    # blockchain
    rpc_server: str
    owner_private_key: str
    invest_contract_address: ChecksumAddress
    invest_contract_abi_path: str

    # server
    host: str
    port: str

    # u_money
    client_id: str

    def __init__(self):
        config = json.load(open("./config.json"))
        # blockchain
        self.rpc_server = config["config"]["blockchain"]["rpc_server"]
        self.owner_private_key = config["config"]["blockchain"]["owner_private_key"]
        self.invest_contract_address = Web3.to_checksum_address(
            config["config"]["blockchain"]["smart_contracts"]["invest_contract"]["address"])
        self.invest_contract_abi_path = config["config"]["blockchain"]["smart_contracts"]["invest_contract"]["path"]

        # server
        self.host = config["config"]["server"]["host"]
        self.port = str(config["config"]["server"]["port"])

        # u_money
        self.client_id = config["config"]["u_money"]["client_id"]

    def get_invest_abi(self):
        f_abi_invest_contract: IO = open(self.invest_contract_abi_path)
        abi_invest_contract = json.load(f_abi_invest_contract)
        return abi_invest_contract
