import os
import re
import json
import base64
import logging
import requests
import xmltodict
from enum import Enum
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key, Encoding, PrivateFormat, NoEncryption, load_der_public_key
)
from cryptography.x509.oid import NameOID
from dataclasses import dataclass, asdict
from typing import Generic, Optional, TypeVar, Any


logger = logging.getLogger(__name__)

T = TypeVar('T')

class DataFormatEnum(Enum):
    JSON = "json"
    XML = "xml"

class ModeOfConnection(Enum):
    PUSH = "PUSH"
    PULL = "PULL"

class CryptoConfig:
    def __init__(self):
        # Default algorithm
        self.algorithm = "SHA256withRSA"

    def get_ega_private_key(self) -> str:
        key_path = os.getenv("GOVESB_PRIVATE_KEY")
        if not key_path:
            logger.error("Environment variable GOVESB_PRIVATE_KEY not set")
            return ""

        logger.info(f"Private key file path: {key_path}, exists: {os.path.exists(key_path)}")

        try:
            with open(key_path, "r", encoding="utf-8") as f:
                data = f.read()
                logger.info(data)
                return data
        except Exception as e:
            logger.error("Exception while reading private key: %s", e)
            return ""

    def get_client_public_key(self) -> str:
        key_path = os.getenv("GOVESB_PUBLIC_KEY")
        if not key_path:
            logger.error("Environment variable GOVESB_PUBLIC_KEY not set")
            return ""

        try:
            with open(key_path, "r", encoding="utf-8") as f:
                data = f.read()
                return data
        except Exception as e:
            logger.error("Exception while reading public key: %s", e)
            return ""

    def get_algorithm(self) -> str:
        return self.algorithm

class JsonFixer:
    # @staticmethod
    # def fix_and_parse_json(bad_json_string:str):
    #     # Escape unescaped control characters: \n, \r, \t
    #     def escape_control_chars(s):
    #         return re.sub(r'(?<!\\)([\n\r\t])', lambda m: '\\' + m.group(1), s)
    #
    #     cleaned = escape_control_chars(bad_json_string)
    #
    #     try:
    #         return json.loads(cleaned)
    #     except json.JSONDecodeError as e:
    #         print("JSON decode failed:", e)
    #         return None

    @staticmethod
    def fix_and_parse_json(bad_json_string):
        # print("Original input:\n", repr(bad_json_string))  # Debug line

        # Escape unescaped control characters
        def escape_control_chars(s):
            return re.sub(r'[\n\r\t]', '', s)
            # return re.sub(r'(?<!\\)([\n\r\t])', lambda m: '\\' + m.group(1), s)

        cleaned = escape_control_chars(bad_json_string)
        # print("\nCleaned JSON string:\n", cleaned)  # Debug line

        try:
            result = json.loads(cleaned)
            # print("\nParsed JSON:\n", result)  # Debug line
            return result
        except json.JSONDecodeError as e:
            print("JSON decode failed:", e)
            return None

@dataclass
class TokenResponse:
    success: Optional[bool] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None

    def __str__(self):
        return (
            f"{{access_token='{self.access_token}', token_type='{self.token_type}', "
            f"expires_in={self.expires_in}, scope='{self.scope}'}}"
        )

@dataclass
class CryptoData(Generic[T]):
    data: Optional[T] = None
    signature: Optional[str] = None

    def __str__(self):
        return f"CryptoData(data={self.data}, signature={self.signature})"

@dataclass
class ESBParameterDto:
    esb_token_uri: Optional[str] = None
    api_code: Optional[str] = None
    push_code: Optional[str] = None
    esb_request_uri: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    key: Optional[str] = None
    format: Optional[DataFormatEnum] = None

@dataclass
class ESBRequest:
    api_code: Optional[str] = None
    push_code: Optional[str] = None
    user_id: Optional[str] = None
    authorization: Optional[str] = None
    signature: Optional[str] = None
    esb_body: Optional[Any] = None
    request_id: Optional[str] = None

@dataclass
class ESBResponse:
    signature: Optional[str] = None
    esb_body: Optional[Any] = None
    request_id: Optional[str] = None
    success: Optional[bool] = None
    message: Optional[str] = None

@dataclass
class RequestData:
    verified: Optional[bool] = None
    esb_body: Optional[str] = None
    request_id: Optional[str] = None

@dataclass
class ResponseData:
    verified_data: Optional[str] = None
    has_data: bool = False
    message: Optional[str] = None

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

class RSAHelper:
    def __init__(self):
        pass  # No need to set provider manually in Python

    @staticmethod
    def generate_key_pair():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def save_private_key_pem(private_key, filename, password=None):
        encoding = serialization.Encoding.PEM
        encryption = NoEncryption()
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())

        with open(filename, "wb") as key_file:
            key_file.write(
                private_key.private_bytes(
                    encoding=encoding,
                    format=PrivateFormat.PKCS8,
                    encryption_algorithm=encryption
                )
            )

    @staticmethod
    def load_private_key_from_str(private_key_str: str):
        private_key_str = private_key_str.replace("-----BEGIN PRIVATE KEY-----", "") \
                                         .replace("-----END PRIVATE KEY-----", "") \
                                         .replace("-----BEGIN RSA PRIVATE KEY-----", "") \
                                         .replace("-----END RSA PRIVATE KEY-----", "") \
                                         .replace("\n", "")
        key_bytes = base64.b64decode(private_key_str)
        return serialization.load_der_private_key(key_bytes, password=None)

    @staticmethod
    def load_public_key_from_str(public_key_str: str):
        public_key_str = public_key_str.replace("-----BEGIN PUBLIC KEY-----", "") \
                                       .replace("-----END PUBLIC KEY-----", "") \
                                       .replace("\n", "")
        key_bytes = base64.b64decode(public_key_str)
        return load_pem_public_key(key_bytes)

    @staticmethod
    def encrypt(plain_text, public_key):
        return base64.b64encode(
            public_key.encrypt(
                plain_text.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        ).decode()

    @staticmethod
    def decrypt(cipher_text, private_key):
        decoded_data = base64.b64decode(cipher_text)
        return private_key.decrypt(
            decoded_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()

    @staticmethod
    def sign(data, private_key, algorithm="SHA256"):
        signature = private_key.sign(
            data.encode(),
            padding.PKCS1v15(),
            getattr(hashes, algorithm)()
        )
        return base64.b64encode(signature).decode()

    @staticmethod
    def verify(data, signature, public_key, algorithm="SHA256"):
        try:
            public_key.verify(
                base64.b64decode(signature),
                data.encode(),
                padding.PKCS1v15(),
                getattr(hashes, algorithm)()
            )
            return True
        except Exception as e:
            logger.error("Verification failed: %s", e)
            return False

    @staticmethod
    def to_pem(obj):
        if isinstance(obj, rsa.RSAPrivateKey):
            return obj.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=NoEncryption()
            ).decode()
        elif hasattr(obj, 'public_bytes'):
            return obj.public_bytes(
                encoding=Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        else:
            raise TypeError("Unsupported object for PEM conversion.")

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, default=str)

    @staticmethod
    def from_json(json_string, cls=dict):
        return json.loads(json_string)

    @staticmethod
    def generate_self_signed_cert(private_key, public_key):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"TZ"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"GOVESB"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"name")
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256(), default_backend())
        return cert

    @staticmethod
    def save_cert(cert, filename):
        with open(filename, "wb") as f:
            f.write(cert.public_bytes(Encoding.PEM))

class ECC:
    FACTORY_TYPE = "EC"
    ALGORITHM = "SHA256withECDSA"
    EC_CURVE_NAME = "secp256k1"

    @staticmethod
    def sign_payload(payload: str, private_key_str: str) -> str:
        try:
            private_key_bytes = base64.b64decode(private_key_str)
            private_key = load_pem_private_key(private_key_bytes, password=None)
            signature = private_key.sign(
                payload.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.error("Error signing payload: %s", e)
            raise

    # @staticmethod
    # def verify_payload(data: str, signature_str: str, public_key_str: str) -> bool:
    #     try:
    #         public_key_bytes = base64.b64decode(public_key_str)
    #         public_key = load_pem_public_key(public_key_bytes)
    #         signature = base64.b64decode(signature_str)
    #
    #         public_key.verify(
    #             signature,
    #             data.encode('utf-8'),
    #             ec.ECDSA(hashes.SHA256())
    #         )
    #         return True
    #     except InvalidSignature:
    #         return False
    #     except Exception as e:
    #         logger.error("Error verifying signature: %s", e)
    #         return False

    @staticmethod
    def verify_payload(data: str, signature_str: str, public_key_str: str) -> bool:
        try:
            # Decode the base64-encoded DER public key
            public_key_bytes = base64.b64decode(public_key_str)
            public_key = load_der_public_key(public_key_bytes)

            # Decode the base64-encoded signature
            signature = base64.b64decode(signature_str)

            # Verify signature
            public_key.verify(
                signature,
                data.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )

            return True

        except InvalidSignature:
            return False
        except Exception as e:
            logger.error("Error verifying signature: %s", e)
            return False

class ESBHelper:

    @staticmethod
    def esb_request(client_id: str, client_secret: str, api_code: str, esb_body: T, format: DataFormatEnum, key: str, esb_token_url: str, esb_request_url: str) -> str:
        token_response = GovESBTokenService.get_esb_access_token(client_id, client_secret, esb_token_url)
        if not token_response.success:
            return "Could not get access token from GovESB"
        return ESBHelper._esb_request(api_code, token_response.access_token, esb_body, format, key, esb_request_url)

    @staticmethod
    def _esb_request(api_code: str, access_token: str, esb_body: T, format: DataFormatEnum, key: str, esb_uri: str) -> str:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": f"application/{format.value}"
        }
        if isinstance(esb_body, dict) or hasattr(esb_body, '__dict__'):
            json_data = json.dumps(esb_body if isinstance(esb_body, dict) else asdict(esb_body))
        else:
            json_data = esb_body

        if format == DataFormatEnum.XML:
            xml_body = xmltodict.unparse({"root": json.loads(json_data)})
            request_payload = ESBHelper.create_signed_request(api_code, access_token, xml_body, format, key)
        else:
            request_payload = ESBHelper.create_signed_request(api_code, access_token, json_data, format, key)

        response = requests.post(esb_uri, headers=headers, data=request_payload.encode("utf-8"))
        return response.text

    @staticmethod
    def create_signed_request(api_code: str, access_token: str, body: str,
                              format: DataFormatEnum, key: str, mode=ModeOfConnection.PULL) -> str:
        req = ESBRequest(
            apiCode=api_code if mode == ModeOfConnection.PULL else None,
            pushCode=api_code if mode == ModeOfConnection.PUSH else None,
            authorization=access_token,
            esbBody=body if format == DataFormatEnum.XML else json.loads(body)
        )
        payload = json.dumps(asdict(req))

        signature = ECC.sign_payload(payload, key)
        signed = CryptoData(data=req.esbBody, signature=signature)

        if format == DataFormatEnum.JSON:
            return json.dumps(asdict(signed))
        elif format == DataFormatEnum.XML:
            xml_obj = {"esbrequest": {"data": req.esbBody, "signature": signature}}
            return xmltodict.unparse(xml_obj)
        else:
            raise ValueError("Unsupported format")

    @staticmethod
    def verify_and_extract_data(received_data: str, format: DataFormatEnum, public_key: str) -> ResponseData:
        response = ResponseData()

        try:
            if format == DataFormatEnum.JSON:
                safe_json_string = JsonFixer.fix_and_parse_json(received_data)
                # data = safe_json_string['data']

                data = json.dumps(safe_json_string, separators=(',', ':'), sort_keys=True)

                signature = safe_json_string['signature']
            else:
                parsed = xmltodict.parse(received_data)
                data = xmltodict.unparse({"data": parsed["esbrequest"]["data"]})
                signature = parsed["esbrequest"]["signature"]

            is_verified = ECC.verify_payload(data, signature, public_key)

            if is_verified:
                response.has_data = True
                response.verified_data = data
            else:
                response.has_data = False
                response.message = "Failed to verify data"

        except Exception as e:
            print('exception', e)
            logger.error(f"Verification failed: {e}")
            response.has_data = False
            response.message = str(e)

        return response

    @staticmethod
    def create_response(esb_body: str, format: DataFormatEnum, key: str, is_success: bool, message: str) -> str:
        response = ESBResponse(
            esbBody=json.loads(esb_body) if format == DataFormatEnum.JSON else esb_body,
            isSuccess=is_success,
            message=message
        )

        payload = json.dumps(asdict(response))
        signature = ECC.sign_payload(payload, key)
        crypto_data = CryptoData(data=response.esbBody, signature=signature)

        if format == DataFormatEnum.JSON:
            return json.dumps(asdict(crypto_data))
        else:
            return xmltodict.unparse({"esbresponse": {"data": response.esbBody, "signature": signature}})
