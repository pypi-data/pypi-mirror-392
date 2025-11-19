# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from io import StringIO
import multiprocessing as mp


class RedirectStdOutMpQueue():
    def __init__(self, response_q: mp.Queue = None) -> None:
        if response_q:
            self._response_q = response_q
            self._string = None
        else:
            self._response_q = None
            self._string = StringIO()

    def write(self, txt):
        if self._response_q:
            self._response_q.put(("out", str(txt)))
        else:
            self._string.write(str(txt))

    def flush(self):
        None

    def get_string(self) -> str:
        return self._string.getvalue() if self._string else ""


class RedirectStdErrMpQueue():
    def __init__(self, response_q: mp.Queue = None) -> None:
        if response_q:
            self._response_q = response_q
            self._string = None
        else:
            self._response_q = None
            self._string = StringIO()

    def write(self, txt):
        if self._response_q:
            self._response_q.put(("err", str(txt)))
        else:
            self._string.write(str(txt))

    def flush(self):
        None

    def get_string(self) -> str:
        return self._string.getvalue() if self._string else ""

class RedirectStdOutArray:
    def __init__(self, output_list, output_lock):
        self.output_list = output_list
        self.output_lock = output_lock
    
    def write(self, s):
        if s:
            with self.output_lock:
                self.output_list.append(("out", s))
    
    def flush(self):
        pass

class RedirectStdErrArray:
    def __init__(self, output_list, output_lock):
        self.output_list = output_list
        self.output_lock = output_lock
    
    def write(self, s):
        if s:
            with self.output_lock:
                self.output_list.append(("err", s))
    
    def flush(self):
        pass