from transformers import AutoTokenizer
from transformers import TFAutoModelForSeq2SeqLM
from transformers import pipeline

checkpoint = "./model/model_finetuned"
tokenizer = AutoTokenizer.from_pretrained("VietAI/vit5-base")
model = TFAutoModelForSeq2SeqLM.from_pretrained(checkpoint, max_length=64, min_length=20)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

def summarizer_wrapper(text):
    result = summarizer(text)
    return result[0]['summary_text']

def get_summary(_list) -> list:
    result = summarizer(_list)
    return [item['summary_text'] for item in result]
