import os

import ray
import torch
from ray import serve

from model import NerModel


@serve.deployment(route_prefix="/ner")
class NerService:
    def __init__(self):
        language_model = os.getenv("LANGUAGE_MODEL", "microsoft/Multilingual-MiniLM-L12-H384")
        self.ner_model = NerModel(language_model)

    async def __call__(self, request):
        return self.ner_model()


ray.init(num_cpus=)
serve.start()
NerService.deploy()
