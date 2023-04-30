from dask.distributed import Client
from .singleton import Singleton


class DaskClient(metaclass=Singleton):
    def __init__(self):
        self.client = Client()

    def get_client(self):
        return self.client
