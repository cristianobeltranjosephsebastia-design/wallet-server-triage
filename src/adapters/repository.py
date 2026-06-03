import json
import os
import threading
from src.domain.account import Account

class JSONAccountRepository:
    def __init__(self, file_path="accounts.json"):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._init_storage()

    def _init_storage(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({
                    "ACC-001": {"titular": "Carlos Mendoza", "saldo": 500000.0, "estado": "ACTIVA", "historial": []},
                    "ACC-002": {"titular": "Ana Gomez", "saldo": 12000.0, "estado": "ACTIVA", "historial": []},
                    "ACC-003": {"titular": "Juan Perez", "saldo": 1000000.0, "estado": "BLOQUEADA", "historial": []}
                }, f, indent=4)

    def find_by_id(self, account_id: str) -> Account:
        with self._lock:
            if not os.path.exists(self.file_path):
                return None
            with open(self.file_path, "r") as f:
                db = json.load(f)
            
            if account_id not in db:
                return None
            
            data = db[account_id]
            return Account(
                account_id=account_id,
                titular=data["titular"],
                saldo=data["saldo"],
                estado=data["estado"],
                historial=data.get("historial", [])
            )

    def save(self, account: Account):
        with self._lock:
            with open(self.file_path, "r") as f:
                db = json.load(f)
            
            db[account.account_id] = account.to_dict()
            
            with open(self.file_path, "w") as f:
                json.dump(db, f, indent=4)
