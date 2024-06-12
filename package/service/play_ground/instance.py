from transformers import AutoTokenizer
from transformers import TFAutoModelForSeq2SeqLM
from transformers import pipeline
from ..version import get_version

summarizer = None

def load_summarizer():
    checkpoint = "./model/" + get_version()
    tokenizer = AutoTokenizer.from_pretrained("VietAI/vit5-base")
    model = TFAutoModelForSeq2SeqLM.from_pretrained(checkpoint, max_length=64, min_length=20)
    global summarizer 
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

def summarizer_wrapper(text):
    result = summarizer(text)
    return result[0]['summary_text']

def summarizer_available():
    if summarizer == None: return False
    return True