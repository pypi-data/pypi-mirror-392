# OCR Layout

Convert OCR JSON to spatial text preserving document layout.

## Installation

```bash
pip install ocr-layout-formatter
```

## Usage

```python
from ocr_layout import Formatter

formatter = Formatter(gap_threshold=40, y_threshold=15)
result = formatter.format(ocr_data)
print(result)
```

### Parameters

- `gap_threshold` (int): Minimum horizontal gap to split text into segments (default: 40)
- `y_threshold` (int): Maximum vertical distance to group texts on same line (default: 15)

### Input Format

```python
ocr_data = [
    {
        "result": [{
            "text_lines": [
                {"text": "Hello", "bbox": [10, 10, 50, 30]},
                {"text": "World", "bbox": [60, 10, 100, 30]}
            ],
            "image_bbox": [0, 0, 200, 300]
        }]
    }
]
```

### Output

```
--- Page 1 ---
Hello World
```

## Logging

Enable logging to see processing details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
