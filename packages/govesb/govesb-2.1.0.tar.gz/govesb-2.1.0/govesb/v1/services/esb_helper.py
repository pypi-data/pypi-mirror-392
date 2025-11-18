import json
import logging
import requests
import xmltodict
from typing import TypeVar, Generic, Optional
from xml.etree import ElementTree as ET
from dataclasses import asdict

from govesb.v1.crypto.ecc import ECC
from govesb.v1.services.token_service import GovESBTokenService
from govesb.v1.models.data import (
    CryptoData, ESBRequest, ESBResponse,
    ResponseData
)

from govesb.v1.models.enums import DataFormatEnum, ModeOfConnection
from govesb.v1.utils.json_fixer import JsonFixer

logger = logging.getLogger(__name__)
T = TypeVar("T")


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
