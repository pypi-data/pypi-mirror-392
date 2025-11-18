import os
import logging

logger = logging.getLogger(__name__)


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
