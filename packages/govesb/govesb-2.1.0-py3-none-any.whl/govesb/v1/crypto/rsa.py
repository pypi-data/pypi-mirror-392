import base64
import json
import logging
import os
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key, Encoding, PrivateFormat, NoEncryption
)
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


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
