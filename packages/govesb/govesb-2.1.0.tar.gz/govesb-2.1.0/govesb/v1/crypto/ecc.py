import base64
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_der_public_key

logger = logging.getLogger(__name__)

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
