import ray
import torch
from ray import serve

from model import NERModel


@serve.deployment(route_prefix="/ner")
class NerService:
    def __init__(self):
        pass
        # self.model = NERModel("")
        # self.model.eval()

    async def __call__(self, request):
        return {"out": "Hello World!"}


ray.init(num_cpus=2)
serve.start()
NerService.deploy()
