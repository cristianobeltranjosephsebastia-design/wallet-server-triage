class GetAccountDetailUseCase:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, account_id: str) -> dict:
        if not account_id:
            raise ValueError("El ID de la cuenta es requerido.")

        account = self.repository.find_by_id(account_id)

        if not account:
            raise LookupError("La cuenta especificada no existe.")

        return account.to_dict()
