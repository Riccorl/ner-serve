import os
from typing import Dict, List

import numpy as np
import onnxruntime as rt
import psutil
import transformer_embedder as tre
from transformer_embedder.tokenizer import ModelInputs


class NerModel:
    def __init__(self, language_model, *args, **kwargs) -> None:
        self.labels = {
            "O": 0,
            "B-PER": 1,
            "I-PER": 2,
            "B-ORG": 3,
            "I-ORG": 4,
            "B-LOC": 5,
            "I-LOC": 6,
            "B-MISC": 7,
            "I-MISC": 8,
        }
        # tokenizer
        self.tokenizer = tre.Tokenizer(language_model)
        # ONNXRuntime stuff
        weights_path = os.getenv("MODEL_PATH", "model/weights.onnx")
        sess_options = rt.SessionOptions()
        sess_options.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_ALL
        # sess_options.execution_mode = rt.ExecutionMode.ORT_PARALLEL
        sess_options.execution_mode = rt.ExecutionMode.ORT_SEQUENTIAL
        logical_cores = kwargs.get("logical_cores", False)
        sess_options.intra_op_num_threads = psutil.cpu_count(logical=logical_cores)
        self.ort_session = rt.InferenceSession(weights_path, sess_options)

    def __call__(self, batch, *args, **kwargs) -> List[Dict]:
        model_inputs = self.collate_fn(batch)
        # filter actual input names
        ort_inputs = {
            model_input.name: model_inputs[model_input.name]
            for model_input in self.ort_session.get_inputs()
        }
        output = self.ort_session.run(None, ort_inputs)
        return self.make_output(model_inputs, output[0])

    def collate_fn(self, batch):
        model_inputs = self.tokenizer([b["tokens"] for b in batch], padding=True, use_spacy=True)
        model_inputs = {
            k: np.asarray(v) if k in self.tokenizer.to_tensor_inputs else v
            for k, v in model_inputs.items()
        }
        return ModelInputs(model_inputs)

    @staticmethod
    def make_output(model_inputs: ModelInputs, model_outputs: np.array) -> List[Dict]:
        service_output = []
        model_outputs: List = np.argmax(model_outputs, axis=-1).tolist()
        for model_input, model_output in zip(model_inputs, model_outputs):
            words = model_input.words
            ner_tags = model_output[1 : len(words)]  # remove CLS and SEP
            service_output.append({w: tag for w, tag in zip(words, ner_tags)})
        return service_output
