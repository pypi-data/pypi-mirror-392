import base64
import logging
import requests
from ..models.data import TokenResponse

logger = logging.getLogger(__name__)

class GovESBTokenService:
    @staticmethod
    def get_esb_access_token(client_id: str, client_secret: str, token_uri: str) -> TokenResponse:
        token_response = TokenResponse(success=False)

        try:
            credentials = f"{client_id}:{client_secret}"
            base64_credentials = base64.b64encode(credentials.encode()).decode()
            headers = {
                "Authorization": f"Basic {base64_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }

            response = requests.post(token_uri, headers=headers, data=data)

            if response.status_code == 200:
                json_response = response.json()
                token_response = TokenResponse(
                    success=True,
                    access_token=json_response.get("access_token"),
                    token_type=json_response.get("token_type"),
                    expires_in=json_response.get("expires_in")
                )
            else:
                logger.error(f"Failed to retrieve token. Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            logger.exception("Exception while retrieving access token:")

        return token_response