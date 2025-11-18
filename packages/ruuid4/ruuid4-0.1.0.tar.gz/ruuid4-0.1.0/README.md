# ruuid4

## Installation
```bash
pip install ruuid4
```

🔗 **GitHub Repository:**
https://github.com/jashan7305/ruuid4

`ruuid4` is a tiny, extremely fast UUID4 generator implemented in rust and exposed to python using PyO3.

## Features
- Generates RFC-4122 compliant UUIDv4 values
- Powered by Rust’s `uuid` crate
- Zero dependencies for Python users

## Functions
- `uuid4()` : Returns a uuid v4 string

## Example

```python
import ruuid4

print(ruuid4.uuid4())
```