# summariser

A tiny, easy-to-use text summarization helper built on HuggingFace transformers.

## Usage
```python
from summariser import summarise

text = "OpenAI released multiple models capable of handling a wide variety of tasks..."
print(summarise(text))
```