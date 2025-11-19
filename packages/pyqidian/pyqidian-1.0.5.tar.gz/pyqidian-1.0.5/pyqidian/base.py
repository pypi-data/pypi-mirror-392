import requests
import datetime
from loguru import logger
import os


def get_sign(timestamp: str) -> str:
    """获取签名
    签名算法说明
    签名算法选择：HmacSHA256

    签名密钥：secretKey，密钥和企业ID相对应，由接口提供方统一提供

    签名内容：corporationId + timestamp

    签名结果编码：base64
    """
    import hmac
    import hashlib
    import base64

    message = f"{os.getenv('CORPORATION_ID')}{timestamp}".encode("utf-8")
    secret = os.getenv("SECRET_KEY").encode("utf-8")
    hash = hmac.new(secret, message, hashlib.sha256)
    sign = base64.b64encode(hash.digest()).decode("utf-8")
    return sign


class base:

    def __init__(self, debug=False):
        self.debug = debug
        self.API_DOMAIN = os.getenv("QIDIAN_API_DOMAIN")
        self.APP_KEY = os.getenv("QIDIAN_APP_KEY")
        self.CORPORATION_ID = os.getenv("QIDIAN_CORPORATION_ID")
        self.BIZ_ID = os.getenv("QIDIAN_BIZ_ID")
        self.SECRET_KEY = os.getenv("QIDIAN_SECRET_KEY")
        self.REPORT_DOMAIN = os.getenv("QIDIAN_REPORT_DOMAIN")
        logger.debug(
            dict(
                msg="初始化参数",
                API_DOMAIN=self.API_DOMAIN,
                APP_KEY=self.APP_KEY,
                CORPORATION_ID=self.CORPORATION_ID,
                BIZ_ID=self.BIZ_ID,
                SECRET_KEY=self.SECRET_KEY,
                REPORT_DOMAIN=self.REPORT_DOMAIN,
            )
        )

    def request(self, api_name, method="GET", **kwargs):
        url = f"https://{self.API_DOMAIN}/{api_name}"
        # 请求头里面携带以下三个字段：corporationId、timestamp(精确到秒)、sign。
        headers = kwargs.get("headers", {})
        headers["corporationId"] = self.CORPORATION_ID
        headers["timestamp"] = str(int(datetime.datetime.now().timestamp()))
        headers["sign"] = get_sign(headers["timestamp"])
        kwargs["headers"] = headers
        params = kwargs.get("params", {})
        params["bizId"] = self.BIZ_ID
        kwargs["params"] = params

        logger.debug(
            dict(
                msg="请求参数",
                url=url,
                method=method,
                headers=headers,
                params=params,
                data=kwargs.get("data", {}),
                json=kwargs.get("json", {}),
            )
        )
        response = requests.request(method, url, **kwargs)
        if response.status_code != 200:
            logger.error(
                dict(
                    msg="请求失败",
                    status_code=response.status_code,
                    response=response.text,
                )
            )
            response.raise_for_status()
        response_data = response.json()
        return self.response(response_data)

    def response(self, data):
        logger.debug(dict(msg="返回值", response=data))
        code = data.get("code", -1)
        requestId = data.get("requestId", "")
        msg = data.get("message", "")
        if code != 0:
            logger.error(
                dict(
                    msg="接口返回错误",
                    code=code,
                    message=msg,
                    response=data,
                    requestId=requestId,
                )
            )
            raise Exception(f"接口返回错误，code={code}, message={msg}")
        return data
