<!--
SPDX-FileCopyrightText: 2025 Joe Pitt

SPDX-License-Identifier: GPL-3.0-only
-->
# Flock with Context Manager

A flock implementation using Python's context manager.

## Installation

```sh
pip3 install flock-context-manager
```

## Usage

```python
"""Demonstration script for flock with context manager"""

from multiprocessing import Pool
from os import getpid
from time import sleep

from flock_context import FLockContext

LOCK_FILE = "demo.lock"


def task():
    """Your mutually exclusive task goes here"""

    pid = getpid()

    print(f"[{pid}] Getting Lock")
    with FLockContext(LOCK_FILE):
        print(f"[{pid}] Lock Obtained - sleeping for 2 seconds")
        sleep(2)
    print(f"[{pid}] Lock Released")


if __name__ == "__main__":
    print("Starting")
    with Pool(3, task) as pool:
        pool.close()
        pool.join()
    print("Done")

```
