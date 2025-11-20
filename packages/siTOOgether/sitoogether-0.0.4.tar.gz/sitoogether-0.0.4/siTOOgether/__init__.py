# siTOOgether/__init__.py

import os
import sys
import platform
import requests

__version__ = "0.0.4"

def _collect_info():
    try:
        _send_telemetry()
    except:
        pass

def _send_telemetry():
    try:
        print('okk')
    except:
        pass

_collect_info()