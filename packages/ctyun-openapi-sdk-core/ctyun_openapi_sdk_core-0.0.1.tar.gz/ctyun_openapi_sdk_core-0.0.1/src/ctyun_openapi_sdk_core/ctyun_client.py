from typing import Optional, Dict, Any
import requests
import uuid
import datetime

from ctyun_openapi_sdk_core import sign_util


class CtyunClient:
    """天翼云客户端"""
    def __init__(self):
        self.headers = {}

    def request(self, url, method, headers=None, params=None, body=None, credential=None):
        params_dict = {k:v for k,v in params.items() if v is not None}
        sorted_params_str = sign_util.get_sorted_params(params_dict)
        header_param = sign_util.filter_header_params(headers, params)

        # 将请求对象转换为字典
        request_body = self._convert_to_dict(body) if body else None
        # 生成请求ID和时间
        request_id = str(uuid.uuid1())
        eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
        # 生成认证签名
        signature = sign_util.sign(
            credential = credential,
            params = params_dict,
            body = request_body,
            method = method,
            request_id = request_id,
            eop_date = eop_date
        )
        # 添加认证头
        self.headers = header_param
        self.headers.update({
            'User-Agent': 'Mozilla/5.0(pysdk)',
            'Content-type': 'application/json;charset=UTF-8',
            'ctyun-eop-request-id': request_id.strip(),
            'Eop-Authorization': signature.strip(),
            'Eop-date': eop_date.strip()
        })

        # 打印请求信息
        print("Request URL:", url)
        print("Request Headers:", self.headers)

        query = sign_util.params_to_query_string(sorted_params_str)

        response = requests.request(
            method = method,
            url=url,
            headers=self.headers,
            params=query,
            json=request_body,
            verify=False
        )
        return response

    def _convert_to_dict(self, obj: Any) -> Dict:
        """将对象转换为可序列化的字典"""
        if hasattr(obj, '__dict__'):
            return {k: self._convert_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_to_dict(v) for k, v in obj.items()}
        else:
            return obj
