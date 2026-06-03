class Account:
    def __init__(self, account_id: str, titular: str, saldo: float, estado: str, historial: list = None):
        self.account_id = account_id
        self.titular = titular
        self.saldo = float(saldo)
        self.estado = estado
        self.historial = historial if historial is not None else []

    def esta_activa(self) -> bool:
        return self.estado == "ACTIVA"

    def tiene_saldo_suficiente(self, monto: float) -> bool:
        return self.saldo >= monto

    def to_dict(self) -> dict:
        return {
            "titular": self.titular,
            "saldo": self.saldo,
            "estado": self.estado,
            "historial": self.historial
        }

