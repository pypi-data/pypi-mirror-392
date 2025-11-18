import base64
import json
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from crypto.Cipher import AES
from crypto.Random import get_random_bytes
# from typing import Optional, Dict
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes




class GovEsbHelper:
    def __init__(self):
        self.client_private_key = ''
        self.encryption_private_key = ''
        self.esb_public_key = ''
        self.client_id = ''
        self.client_secret = ''
        self.esb_token_url = ''
        self.esb_engine_url = ''
        self.nida_user_id = ''
        self.api_code = ''
        self.request_body = None
        self.format = 'json'
        self.access_token = None

    def get_access_token(self):
        auth = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.esb_token_url, data=data, headers=headers)
        token_response = response.json()
        if response.status_code == 200 and "access_token" in token_response:
            self.access_token = token_response["access_token"]
            return token_response
        raise Exception("Could not get access token from ESB")

    def sign_payload_ecc(self, payload: str) -> str:
        key = serialization.load_der_private_key(
            base64.b64decode(self.client_private_key),
            password=None,
            backend=default_backend()
        )
        signature = key.sign(payload.encode(), ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode()

    def verify_payload_ecc(self, data: str, signature: str) -> bool:
        pub_key = serialization.load_der_public_key(
            base64.b64decode(self.esb_public_key),
            backend=default_backend()
        )
        try:
            pub_key.verify(
                base64.b64decode(signature),
                data.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    def encrypt_ecies(self, plain_data: str) -> str:
        pub_key = serialization.load_der_public_key(
            base64.b64decode(self.esb_public_key),
            backend=default_backend()
        )
        ephemeral_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        shared_key = ephemeral_key.exchange(ec.ECDH(), pub_key)
        aes_key = shared_key[:16]

        cipher = AES.new(aes_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plain_data.encode())

        return json.dumps({
            "encryptedKey": base64.b64encode(
                ephemeral_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            ).decode(),
            "encryptedData": base64.b64encode(cipher.nonce + ciphertext + tag).decode()
        })

    def decrypt_ecies(self, encrypted_aes_key: str, encrypted_data: str) -> str:
        priv_key = serialization.load_der_private_key(
            base64.b64decode(self.encryption_private_key),
            password=None,
            backend=default_backend()
        )
        aes_key = priv_key.private_numbers().private_value.to_bytes(32, 'big')[:16]
        raw = base64.b64decode(encrypted_data)
        nonce, ciphertext, tag = raw[:16], raw[16:-16], raw[-16:]
        cipher = AES.new(aes_key, AES.MODE_EAX, nonce)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted.decode()

    def convert_pem(self, pem_string: str, is_private: bool = False) -> bytes:
        if is_private:
            return base64.b64decode(
                pem_string.replace("-----BEGIN EC PRIVATE KEY-----", "")
                .replace("-----END EC PRIVATE KEY-----", "")
                .replace("\n", "")
            )
        return base64.b64decode(
            pem_string.replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "")
        )
