import torch
import transformer_embedder as tre
from torch import nn


class NERModel(nn.Module):
    def __init__(self, language_model, *args, **kwargs) -> None:
        super().__init__()
        self.labels = {}
        # tokenizer
        self.tokenizer = tre.Tokenizer(language_model)
        # model itself
        self.language_model = tre.TransformerEmbedder(
            language_model,
            subtoken_pooling="mean",
            output_layer="sum",
        )
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.language_model.hidden_size, len(self.labels), bias=False)

    def forward(self, inputs, *args, **kwargs) -> torch.Tensor:
        x = self.language_model(**self.collate_fn(inputs)).word_embeddings
        x = self.dropout(x)
        x = self.classifier(x)
        return x

    def collate_fn(self, batch):
        batch_x = self.tokenizer(
            [b["tokens"] for b in batch], return_tensors=True, padding=True, use_spacy=True
        )
        return batch_x
