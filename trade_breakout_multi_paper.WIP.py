from ib_insync import *
import math
import csv
import os
import atexit
from datetime import datetime, timezone

# --- monitoring / logging ---
from infra.logger import setup_logger
from infra.metrics import load_metrics, inc
logger = setup_logger('logs/bot.log')
metrics = load_metrics()
SHUTTING_DOWN = False
SCRIPT_DONE = False
_EVENTS_BOUND = False

def _on_exit():
    global SHUTTING_DOWN
