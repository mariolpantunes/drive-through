import time
import argparse


def check_positive_number(number):
    ivalue = int(number)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % number)
    return ivalue


def check_port(port, base=1024):
    ivalue = int(port)
    if ivalue <= base:
        raise argparse.ArgumentTypeError("%s is an invalid port value" % port)
    return ivalue


def work(seconds):
    time.sleep(seconds)
