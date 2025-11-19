from .ctyun_client import CtyunClient


class ClientConfig:
    def __init__(self, endpoint:str, access_key_id: str, access_key_secret: str):
        self.endpoint = endpoint
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
