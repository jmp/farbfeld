# farbfeld.py

[![Build Status](https://travis-ci.org/jmp/farbfeld.svg?branch=master)](https://travis-ci.org/jmp/farbfeld)
[![codecov](https://codecov.io/gh/jmp/farbfeld/branch/master/graph/badge.svg)](https://codecov.io/gh/jmp/farbfeld)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/jmp/farbfeld.svg)](https://lgtm.com/projects/g/jmp/farbfeld/context:python)

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
    data = farbfeld.read(f)
```

Note that since farbfeld stores pixel components as 16-bit
unsigned integers, you may have to normalize them or scale
them to a different range (e.g. 8-bit). For example, using
NumPy and Matplotlib:

```python
import farbfeld
import numpy as np
import matplotlib.pyplot as plt

with open('image.ff', 'rb') as f:
    data = farbfeld.read(f)
    data_8bit = np.array(data).astype(np.uint8)
    plt.imshow(data_8bit, interpolation='nearest')
    plt.show()
```

## Source code

The source code is available on GitHub:
https://github.com/jmp/farbfeld
