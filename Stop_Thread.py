import ctypes
import inspect
import time
from threading import Thread

def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def Stop_Thread(thread):
    print(f'\nt -> {thread}')
    print(f'\nthread.ident -> {thread.ident}')
    _async_raise(thread.ident, SystemExit)
    thread.join()