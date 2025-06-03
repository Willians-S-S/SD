# SentimentClassifier.py
import torch
from transformers import BertModel

class SentimentClassifier(torch.nn.Module):
    def __init__(self, n_classes, pre_trained_model_path_or_name='neuralmind/bert-large-portuguese-cased'):
        super(SentimentClassifier, self).__init__()
        print(f"INFO [SentimentClassifier] Inicializando BertModel a partir de: {pre_trained_model_path_or_name}")
        self.bert = BertModel.from_pretrained(pre_trained_model_path_or_name, return_dict=False)
        self.drop = torch.nn.Dropout(p=0.3)
        self.out = torch.nn.Linear(self.bert.config.hidden_size, n_classes)
        print(f"INFO [SentimentClassifier] Camada de saída para {n_classes} classes criada.")

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        output = self.drop(pooled_output)
        return self.out(output)