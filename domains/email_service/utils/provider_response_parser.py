class ProviderResponseParser:
    @staticmethod
    def parse_smtp(response_text):
        """
        Simples parser para mensagens de resposta SMTP.
        """
        # Em uma implementação real, usaria regex para extrair código e mensagem.
        # Ex: "250 OK" -> code: 250, message: "OK"
        try:
            parts = response_text.split(' ', 1)
            code = int(parts[0])
            message = parts[1] if len(parts) > 1 else ""
            return {
                "response_code": code,
                "response_message": message,
                "server_response": response_text
            }
        except (ValueError, IndexError):
            return {
                "response_code": 0,
                "response_message": "Unknown",
                "server_response": response_text
            }
