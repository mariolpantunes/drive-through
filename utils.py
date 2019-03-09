import time
import argparse

ORDER = 0
REQ_TASK = 1
TASK_READY = 2
PICKUP = 3

def work(seconds):
    time.sleep(seconds)
