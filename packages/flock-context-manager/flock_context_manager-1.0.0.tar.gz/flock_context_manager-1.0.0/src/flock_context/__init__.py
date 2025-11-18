# SPDX-FileCopyrightText: 2025 Joe Pitt
#
# SPDX-License-Identifier: GPL-3.0-only

"""A flock implementation using Python's context manager."""

from os.path import abspath
from time import sleep, time
from types import TracebackType
from typing import Optional
import fcntl
import os

__title__ = "flock-context-manager"
__description__ = "A flock implementation using Python's context manager."
__author__ = "Joe Pitt"
__copyright__ = "Copyright 2025, Joe Pitt"
__email__ = "Joe.Pitt@joepitt.co.uk"
__license__ = "GPL-3.0-only"
__maintainer__ = "Joe Pitt"
__status__ = "Production"
__version__ = "1.0.0"


class FLockContext:
    """A file lock with context manager support"""

    file_path: str = None
    file_descriptor: int = None

    def __init__(self, lock_file: str, timeout: Optional[float] = None):
        lock_file = abspath(lock_file)
        open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
        file_descriptor = os.open(lock_file, open_mode)
        start_time = time()
        while timeout is None or time() < start_time + timeout:
            try:
                # Get an exclusive, non-binding lock
                fcntl.flock(file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                sleep(0.5)
                continue
            self.file_descriptor = file_descriptor
            self.file_path = lock_file
            break

        if self.file_descriptor is None:
            os.close(file_descriptor)
            raise ValueError(f"Failed to acquire lock on {lock_file}")

    def __enter__(self) -> "FLockContext":
        return self

    def __exit__(
        self,
        _exception_type: Optional[type[BaseException]],
        _exception_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> None:
        if self.file_descriptor is None:
            raise ValueError("Do not have lock")
        fcntl.flock(self.file_descriptor, fcntl.LOCK_UN)
        os.close(self.file_descriptor)
