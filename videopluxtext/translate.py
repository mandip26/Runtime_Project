from transformers import AutoTokenizer, pipeline, AutoModel
import torch
from dotenv import load_dotenv
import os
from transformers.utils import logging
from typing import Optional
import asyncio

logging.set_verbosity_error()

load_dotenv()

class TranslateMassage:

    def __init__(self):
        self.model_name = "videopluxtext/cache/models--facebook--nllb-200-distilled-600M/snapshots/f8d333a098d19b4fd9a8b18f94170487ad3f821d"
        self.model = AutoModel.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.translator: Optional[object] = None

    async def load_pipline(self):
        self.translator = pipeline(
            task="translation",
            model="facebook/nllb-200-distilled-600M",
            torch_dtype=torch.bfloat16,
        )

    def translate_input(self, text, request_language):
        language_model = {
            "English": "eng_Latn",
            "Hindi": "hin_Deva",
            "Bengali": "ben_Beng",
            "Gujarati": "guj_Gujr",
            "Marathi": "mar_Deva",
            "Maithili": "mai_Deva",
            "Malayalam": "mal_Mlym",
            "Tamil": "tam_Taml",
            "Telugu": "tel_Telu",
        }

        targetModel = language_model.get(request_language)

        if self.translator is None:
            raise ValueError("Translator pipeline has not been initialized. Call load_pipline first.")

        text_translated = self.translator(
            text, src_lang="eng_Latn", tgt_lang=targetModel
        )

        return text_translated


if __name__ == "__main__":
    async def main():
        translateMassage = TranslateMassage()
        await translateMassage.load_pipline()  # Initialize the pipeline
        result = translateMassage.translate_input("Hello, how are you?", "Hindi")
        print(result)

    asyncio.run(main())
