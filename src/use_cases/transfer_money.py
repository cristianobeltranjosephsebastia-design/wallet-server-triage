import datetime

class TransferMoneyUseCase:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, origin_id: str, destiny_id: str, amount: float) -> dict:
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise ValueError("El monto debe ser un número válido.")

        if amount <= 0:
            raise ValueError("El monto de la transferencia debe ser mayor a cero.")

        origin_account = self.repository.find_by_id(origin_id)
        destiny_account = self.repository.find_by_id(destiny_id)

        if not origin_account or not destiny_account:
            raise LookupError("Una o ambas cuentas no existen.")

        if not origin_account.esta_activa():
            raise PermissionError("La cuenta de origen no está activa.")
        
        if not destiny_account.esta_activa():
            raise PermissionError("La cuenta de destino se encuentra bloqueada o inactiva.")

        if not origin_account.tiene_saldo_suficiente(amount):
            raise ValueError("Fondos insuficientes para completar la transacción.")

        origin_account.saldo -= amount
        destiny_account.saldo += amount

        fecha = str(datetime.datetime.now())
        origin_account.historial.append({"tipo": "DEBITO", "monto": amount, "target": destiny_id, "fecha": fecha})
        destiny_account.historial.append({"tipo": "CREDITO", "monto": amount, "target": origin_id, "fecha": fecha})

        self.repository.save(origin_account)
        self.repository.save(destiny_account)

        return {"status": "SUCCESS", "message": "Transferencia procesada de forma segura"}
