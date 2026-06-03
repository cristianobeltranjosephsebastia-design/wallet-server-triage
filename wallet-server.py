import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Importamos nuestros componentes de la Arquitectura Limpia
from src.adapters.repository import JSONAccountRepository
from src.use_cases.get_balance import GetAccountDetailUseCase
from src.use_cases.transfer_money import TransferMoneyUseCase
from src.infrastructure.middleware import SecurityMiddleware

# Instanciamos el repositorio único (con su Mutex compartido)
repo = JSONAccountRepository()

class PaymentGatewayAPI(BaseHTTPRequestHandler):

    def _response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        url_parsed = urlparse(self.path)
        path = url_parsed.path
        query = parse_qs(url_parsed.query)

        if path == "/api/v1/accounts/detail":
            try:
                account_id = query.get("id")[0] if query.get("id") else None
                use_case = GetAccountDetailUseCase(repo)
                result = use_case.execute(account_id)
                return self._response(result, 200)
            except ValueError as e:
                return self._response({"error": str(e)}, 400)
            except LookupError as e:
                return self._response({"error": str(e)}, 404)
            except Exception:
                return self._response({"error": "Internal Server Error"}, 500)
        
        self._response({"msg": "Gateway Ready"}, 200)

    def do_POST(self):
        url_parsed = urlparse(self.path)
        path = url_parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self._response({"error": "Bad Request JSON"}, 400)

        # RUTA: Transferencias
        if path == "/api/v1/transactions/transfer":
            try:
                use_case = TransferMoneyUseCase(repo)
                result = use_case.execute(
                    origin_id=payload.get("desde"),
                    destiny_id=payload.get("hacia"),
                    amount=payload.get("monto")
                )
                return self._response(result, 200)
            except ValueError as e:
                return self._response({"error": str(e)}, 400)
            except PermissionError as e:
                return self._response({"error": str(e)}, 403)
            except LookupError as e:
                return self._response({"error": str(e)}, 404)
            except Exception:
                return self._response({"error": "Error inesperado en el core"}, 500)

        # RUTA: Administrativa Protegida con Middleware
        elif path == "/api/v1/accounts/admin/bypass-status":
            if not SecurityMiddleware.is_authorized(self.headers):
                return self._response({"error": "No autorizado. Token de administración inválido."}, 401)

            acc_id = payload.get("id")
            new_status = payload.get("status")

            account = repo.find_by_id(acc_id)
            if account:
                account.estado = new_status
                repo.save(account)
                return self._response({"status": "CHANGED", "message": f"Estado cambiado a {new_status}"}, 200)
            
            return self._response({"error": "Cuenta no encontrada"}, 404)

        self._response({"error": "Endpoint inválido"}, 404)

def run(port=8500):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, PaymentGatewayAPI)
    print(f"💰 Core Bancario / API Gateway corriendo en puerto {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()
