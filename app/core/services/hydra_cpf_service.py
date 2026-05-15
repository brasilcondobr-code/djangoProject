import requests
import logging
from requests.exceptions import RequestException

# Configure logging for HydraCPF service
logger = logging.getLogger(__name__)

# Configuration - In production, these should be in settings.py/env
HYDRACPF_API_KEY = "sk_live_TDogmdQoMrPF4GF6snsID3S83GAklhQvVFqVxWnfenU"
HYDRACPF_URL = "https://api.hydracpf.com/v1/cpf"

def consult_cpf(cpf):
    """
    Consults the HydraCPF API to validate and retrieve CPF status.
    
    Args:
        cpf (str): The CPF number (digits only).
        
    Returns:
        dict: Data from API if successful, None otherwise.
    """
    if not cpf or len(cpf) != 11:
        logger.warning(f"Invalid CPF length for API consultation: {cpf}")
        return None

    try:
        headers = {
            "x-api-key": HYDRACPF_API_KEY,
            "Content-Type": "application/json",
        }

        logger.info(f"Consulting HydraCPF API for CPF: {cpf}")
        response = requests.get(
            f"{HYDRACPF_URL}/{cpf}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"HydraCPF API Success response for {cpf}: {data}")
            
            # If the API returns 200 but all key fields are None, treat it as not found
            if not data.get("situation") and not data.get("name"):
                return {
                    "situation": "Não Encontrado",
                    "regular": None,
                    "death": None,
                }

            return {
                "cpf": data.get("cpf"),
                "name": data.get("nome"),
                "situation": data.get("situacao"),
                "regular": data.get("regular"),
                "death": data.get("obito"),
                "birth_date": data.get("data_nascimento"),
                "mother_name": data.get("nome_mae"),
                "sex": data.get("sexo"),
            }
        elif response.status_code == 404:
            try:
                data = response.json()
                if data.get("detail", {}).get("code") == "CPF_NOT_FOUND":
                    return {
                        "situation": "Não Encontrado",
                        "regular": None,
                        "death": None,
                    }
            except Exception:
                pass

        logger.error(f"HydraCPF API returned error {response.status_code}: {response.text}")
        return {"error": response.status_code, "text": response.text}

    except RequestException as e:
        logger.error(f"Network error during HydraCPF API consultation: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during HydraCPF API consultation: {str(e)}")
        return None
