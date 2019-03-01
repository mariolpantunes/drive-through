# coding: utf-8

import zmq
import logging
import argparse
import random
import pickle
import math
from ipaddress import ip_address
from utils import check_port, work

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')


def main(args, mu=0.01, sigma=0.005):
    # create a logger for the client
    logger = logging.getLogger('Client')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://' + str(args.ip) + ':' + str(args.port))

    for i in range(10):
        logger.info('Request some remote function (RPC)')
        # use pickle to dump a object
        p = pickle.dumps('rpc '+str(i))
        # send it
        socket.send(p)

        # receive a compress object
        p = socket.recv()
        # use pickle to load the object
        o = pickle.loads(p)
        logger.info('Received %s', o)

        # generate the number of seconds the work will take
        seconds = math.fabs(random.gauss(mu, sigma))
        logger.info('Client will work for %f seconds', seconds)
        # work(sleep) for the previous amount of seconds
        work(seconds)

    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Drive-through')
    parser.add_argument('--ip', type=ip_address, help='ip address', default='127.0.0.1')
    parser.add_argument('--port', type=check_port, help='ip port', default=5002)
    args = parser.parse_args()
    main(args)
