from transformers import pipeline

def summarise(text: str, model: str = "facebook/bart-large-cnn"):
    """Return a clean summary for the given text using a default BART model."""
    summarizer = pipeline("summarization", model=model)
    result = summarizer(text, max_length=150, min_length=30, do_sample=False)
    return result[0]["summary_text"]