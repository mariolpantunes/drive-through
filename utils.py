import time
import argparse


def check_positive_number(number):
    return number > 0


def check_port(port, base=1024):
    ivalue = int(port)
    if ivalue <= base:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def work(seconds):
    time.sleep(seconds)
