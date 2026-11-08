# units-converter

Convert quantities between units of the same dimension.

```python
from units import convert, convert_string

convert(5, "km", "mi")  # 3.1068...
convert_string("100 C to F")  # 212.0
```

Supported dimensions: length (base `m`), mass (base `kg`), temperature (`C`, `F`, `K`).

Run the tests with `python -m pytest`.
