# Afaan Oromo Tokenizer



Afaan_oromo_tokenizer is a linguistically informed and computationally efficient tokenizer for **Afaan Oromo**, one of the most widely spoken low-resource languages in Africa.  


-------------------------------------------------


 - While tokenizers exist for major languages (English, Chinese, etc.), Afan Oromo lacks robust open-source tokenization tools.  
 - Afaan_oromo_tokenizer bridges that gap, facilitating NLP research for afaan Oromo.


---

## Features

- Included: **BPE**, **Unigram**, **WordPiece**
- Trained on **14 million tokens**
- Total unique tokens in dataset: **420,000**
- Vocabulary size for each tokenizer type: **55,000**

---

## Installation

```bash
pip install afaanoromo-tokenizer

```
## Usage

```python
from afaanoromo_tokenizer import ao_tokenizer

# Example text
text = "Afaanni Oromoo afaan saba guddaati!"

# --- BPE tokenizer ---
bpe_tokenizer = ao_tokenizer("bpe")
bpe_encoded = bpe_tokenizer.encode(text)

print("BPE tokens:", bpe_encoded.tokens)
print("BPE ids:", bpe_encoded.ids)

bpe_decoded = bpe_tokenizer.decode(bpe_encoded.ids)
print("BPE decoded:", bpe_decoded)

# --- Unigram tokenizer ---
unigram_tokenizer = ao_tokenizer("unigram")
unigram_encoded = unigram_tokenizer.encode(text)

print("Unigram tokens:", unigram_encoded.tokens)
print("Unigram ids:", unigram_encoded.ids)

unigram_decoded = unigram_tokenizer.decode(unigram_encoded.ids)
print("Unigram decoded:", unigram_decoded)

# --- WordPiece tokenizer ---
wordpiece_tokenizer = ao_tokenizer("wordpiece")
wordpiece_encoded = wordpiece_tokenizer.encode(text)

print("WordPiece tokens:", wordpiece_encoded.tokens)
print("WordPiece ids:", wordpiece_encoded.ids)

wordpiece_decoded = wordpiece_tokenizer.decode(wordpiece_encoded.ids)
print("WordPiece decoded:", wordpiece_decoded)

```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
