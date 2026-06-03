class SecurityMiddleware:
    @staticmethod
    def is_authorized(headers) -> bool:
        admin_token = headers.get("X3203084ADMIN")
        return admin_token == "3203084"
