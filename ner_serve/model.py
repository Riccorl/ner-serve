import os
from typing import List

import numpy as np
import onnxruntime as rt
import transformer_embedder as tre
from transformer_embedder.tokenizer import ModelInputs

from objects import WordOut, DocumentOut


class NerModel:
    def __init__(self, *args, **kwargs) -> None:
        self.labels = {
            0: "O",
            1: "B-PER",
            2: "I-PER",
            3: "B-ORG",
            4: "I-ORG",
            5: "B-LOC",
            6: "I-LOC",
            7: "B-MISC",
            8: "I-MISC",
        }
        # params
        language_model = os.getenv("LANGUAGE_MODEL", "microsoft/Multilingual-MiniLM-L12-H384")
        # tokenizer
        self.tokenizer = tre.Tokenizer(language_model)
        # ONNXRuntime stuff
        weights_path = os.getenv("MODEL_PATH", "model/weights.onnx")
        sess_options = rt.SessionOptions()
        sess_options.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.execution_mode = rt.ExecutionMode.ORT_SEQUENTIAL
        sess_options.intra_op_num_threads = os.getenv("NUM_THREADS", 1)
        self.ort_session = rt.InferenceSession(weights_path, sess_options)

    def __call__(self, batch, *args, **kwargs) -> List[DocumentOut]:
        model_inputs = self.collate_fn(batch)
        # filter actual input names
        ort_inputs = {
            model_input.name: model_inputs[model_input.name]
            for model_input in self.ort_session.get_inputs()
        }
        output = self.ort_session.run(None, ort_inputs)
        return self.make_output(model_inputs, output[0])

    def collate_fn(self, batch):
        model_inputs = self.tokenizer(batch, padding=True, use_spacy=True)
        model_inputs = {
            k: np.asarray(v) if k in self.tokenizer.to_tensor_inputs else v
            for k, v in model_inputs.items()
        }
        return ModelInputs(model_inputs)

    def make_output(self, model_inputs: ModelInputs, model_outputs: np.array) -> List[DocumentOut]:
        service_output = []
        model_outputs: List = np.argmax(model_outputs, axis=-1).tolist()
        for words, model_output in zip(model_inputs.words, model_outputs):
            words = words[1:] # remove CLS and SEP
            ner_tags = model_output[1 : len(words)]  # remove CLS and SEP
            tokens = [
                WordOut(index=i, text=w, ner_tag=self.labels[tag])
                for i, (w, tag) in enumerate(zip(words, ner_tags))
            ]
            service_output.append(DocumentOut(tokens=tokens))
        return service_output
