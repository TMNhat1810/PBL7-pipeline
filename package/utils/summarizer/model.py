from transformers import AutoTokenizer
from transformers import TFAutoModelForSeq2SeqLM
from transformers import pipeline

def get_model(version: str):
    checkpoint = "./model/" + version
    tokenizer = AutoTokenizer.from_pretrained("VietAI/vit5-base")
    model = TFAutoModelForSeq2SeqLM.from_pretrained(checkpoint, max_length=64, min_length=20)
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
    return summarizer

def get_summary(_list, version) -> list:
    summarizer = get_model(version)
    result = summarizer(_list)
    return [item['summary_text'] for item in result]
