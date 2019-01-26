# farbfeld.py

This is a small Python module for extracting pixel data from
farbfeld images: https://tools.suckless.org/farbfeld/

Currently it only has one public function, `farbfeld.read`.
It returns the pixels as row by row, column by column as
a nested list.

## Installation

The module is available on PyPI: https://pypi.org/project/farbfeld/

You can install it with `pip`:

    pip install farbfeld

## Usage

To read an image, open the desired file and read the pixels
from it using `farbfeld.read`:

```python
import farbfeld

with open('image.ff', 'rb') as f:
    data = farbfeld.read(f.read())
```

Since farbfeld stores pixel components as 16-bit unsigned
integers, it may be useful in some cases to normalize them
to the [0, 1] range. Then you can visualize it, for example
using `matplotlib`:

```python
import farbfeld
import matplotlib.pyplot as plt

with open('image.ff', 'rb') as f:
    data = farbfeld.read(f.read(), normalize=True)
    plt.imshow(data, interpolation='nearest')
    plt.show()
```
