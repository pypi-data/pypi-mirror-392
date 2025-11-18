# Codexify

Codexify is a lightweight Python library for transforming text into a custom encoded form.  
It applies a simple character-shifting algorithm to letters and digits while keeping all other symbols unchanged.

This library is intended for simple text encoding, experiments, or as a foundation for custom cipher logic.

---

## Usage example

from Codexify import Converter

converter = Converter()

text = "hello world"

encoded = converter.convert_text(text)

print(encoded)

---

- Encodes letters by shifting them to the next character  
- Encodes digits in the same way  
- Other characters remain unchanged  
- Simple API  
- No dependencies  
- Works on Python 3.7+

---

## Installation

```bash
pip install Codexify