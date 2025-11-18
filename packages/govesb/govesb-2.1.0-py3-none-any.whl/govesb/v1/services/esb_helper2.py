import json
import logging
import requests
import xml.etree.ElementTree as ET
import xmltodict
from dataclasses import asdict
from ..services.token_service import GovESBTokenService
from ..crypto.ecc import ECC
from ..models.data import (
    ResponseData
)
from ..models.enums import (
    ModeOfConnection, DataFormatEnum
)
from govesb.v1.utils.json_fixer import JsonFixer

logger = logging.getLogger(__name__)

class ESBHelper2:
    DEFAULT_HASH_ALGORITHM = "SHA1withRSA"


    @staticmethod
    def esb_request_with_token(client_id, client_secret, api_code, esb_body, format, key, token_url, request_url):
        token_response = GovESBTokenService.get_esb_access_token(client_id, client_secret, token_url)
        if not token_response.success:
            return "Could not get access token from GovESB"
        return ESBHelper2.esb_request(api_code, token_response.access_token, esb_body, format, key, request_url)

    @staticmethod
    def esb_request(api_code, access_token, esb_body, format, key, url):
        if isinstance(esb_body, dict) or hasattr(esb_body, '__dict__'):
            esb_body_json = json.dumps(esb_body if isinstance(esb_body, dict) else asdict(esb_body))
        else:
            esb_body_json = esb_body

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": f"application/{format.value}"
        }

        if format == DataFormatEnum.XML:
            esb_body_xml = xmltodict.unparse(json.loads(esb_body_json))
            payload = ESBHelper2.create_request(api_code, access_token, esb_body_xml, format, key, ModeOfConnection.PULL)
        else:
            payload = ESBHelper2.create_request(api_code, access_token, esb_body_json, format, key, ModeOfConnection.PULL)

        response = requests.post(url, data=payload.encode("utf-8"), headers=headers)
        return response.text

    @staticmethod
    def esb_push_request(push_code, access_token, esb_body, format, key, url):
        headers = {
            "Authorization": access_token,
            "Content-Type": f"application/{format.value}"
        }

        payload = ESBHelper2.create_request(push_code, access_token, esb_body, format, key, ModeOfConnection.PUSH)
        response = requests.post(url, data=payload.encode("utf-8"), headers=headers)
        return response.text

    @staticmethod
    def create_request(api_code, access_token, esb_body, format, key, mode):
        request_dict = {
            "apiCode": api_code if mode == ModeOfConnection.PULL else None,
            "pushCode": api_code if mode == ModeOfConnection.PUSH else None,
            "authorization": access_token if mode == ModeOfConnection.PULL else None,
            "esbBody": esb_body if format == DataFormatEnum.XML else json.loads(esb_body)
        }

        request_dict = {k: v for k, v in request_dict.items() if v is not None}

        if format == DataFormatEnum.JSON:
            json_payload = json.dumps(request_dict)
            signature = ECC.sign_payload(json_payload, key)
            signed = {"data": request_dict, "signature": signature}
            return json.dumps(signed)

        elif format == DataFormatEnum.XML:
            xml_data = xmltodict.unparse({"data": request_dict})
            signature = ECC.sign_payload(xml_data, key)
            signed = {"esbrequest": {"data": request_dict, "signature": signature}}
            return xmltodict.unparse(signed)

        raise ValueError("Unsupported format")

    @staticmethod
    def sign_payload(payload, key, format_type):
        try:
            signature = ECC.sign_payload(payload, key)
            return signature
        except Exception as e:
            logger.error("error in signature", exc_info=e)
            return "error in signature"

    @staticmethod
    def extract_real_data(xml_str):
        start = xml_str.find("<data>")
        end = xml_str.find("</data>") + len("</data>")
        return xml_str[start:end].strip()

    @staticmethod
    def parse_xml(xml_str):
        return ET.fromstring(xml_str)

    @staticmethod
    def verify_signed_payload(received_data, format_enum, public_key):
        try:
            if format_enum == DataFormatEnum.JSON:
                data = json.loads(received_data)
                payload = json.dumps(data.get("data"))
                signature = data.get("signature")
                return ECC.verify_payload(payload, signature, public_key)
            elif format_enum == DataFormatEnum.XML:
                data = ESBHelper2.extract_real_data(received_data)
                parsed = ET.fromstring(received_data)
                signature = parsed.find("signature").text
                return ECC.verify_payload(data, signature, public_key)
        except Exception as e:
            logger.error("Error verifying payload", exc_info=e)
            return False

    @staticmethod
    def verify_and_extract_data(received_data: str, format_enum, public_key: str):
        result = ResponseData()
        try:
            if format_enum == DataFormatEnum.JSON:
                safe_json_string = JsonFixer.fix_and_parse_json(received_data)
                data = safe_json_string['data']
                signature = safe_json_string['signature']
                verified = ECC.verify_payload(data, signature, public_key)
            else:
                data = ESBHelper2.extract_real_data(received_data)
                doc = ET.fromstring(received_data)
                signature = doc.find("signature").text
                verified = ECC.verify_payload(data, signature, public_key)

            if verified:
                result.has_data = True
                result.verified_data = data
            else:
                result.has_data = False
                result.message = "failed to verify response data"
        except Exception as e:
            logger.error("Verification failed", exc_info=e)
            result.has_data = False
            result.message = str(e)

        return result

