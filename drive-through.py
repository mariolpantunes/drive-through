# coding: utf-8

import zmq
import logging
import argparse
import threading
import zlib
import pickle
import random
import math
from ipaddress import ip_address
from utils import check_port, check_positive_number, work

# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')


class Worker(threading.Thread):
    def __init__(self, context, i, backend, mu=0.01, sigma=0.005):
        # call the constructor form the parent class
        threading.Thread.__init__(self)

        # create a socket to connect to the backend and serve request
        # the socket type is Reply
        self.socket = context.socket(zmq.REP)
        self.socket.connect(backend)

        # store the necessary inputs
        self.logger = logging.getLogger('Worker '+str(i))
        self.mu = mu
        self.sigma = sigma

    def run(self):

        self.logger.info('Start working')
        while True:
            # receive a compress object
            z = self.socket.recv()
            # decompress it
            p = zlib.decompress(z)
            # use pickle to load the object
            o = pickle.loads(p)

            # print the object
            self.logger.info('Worker received %s', o)
            # generate the number of seconds the work will take
            seconds = math.fabs(random.gauss(self.mu, self.sigma))
            self.logger.info('Will work for %f seconds', seconds)
            # work(sleep) for the previous amount of seconds
            work(seconds)

            # use pickle to dump a object
            p = pickle.dumps('ACK')
            # compress the object
            z = zlib.compress(p)
            # send it
            self.socket.send(z)
        # close the socket
        self.socket.close()


class DriveThrough(threading.Thread):
    def __init__(self, frontend, n_workers, backend='inproc://backend'):
        # call the constructor form the parent class
        threading.Thread.__init__(self)

        # create a logger for the main thread
        self.logger = logging.getLogger('Drive-through')

        # store the address for communication with the outside world and the workers
        # frontend will be a TCP scoket
        self.frontend_addr = frontend
        # backend will be a inproc socket (socket for threads)
        self.backend_addr = backend
        self.n_workers = n_workers

    def run(self):
        # setup zmq frontend and backend sockets
        # create a shared ZMQ context
        self.logger.info('Setup ZMQ')
        context = zmq.Context()

        # frontend for clients (socket type Router)
        frontend = context.socket(zmq.ROUTER)
        frontend.bind(self.frontend_addr)

        # backend for workers (socket type Dealer)
        backend = context.socket(zmq.DEALER)
        backend.bind(self.backend_addr)

        # Setup workers
        workers = []
        for i in range(self.n_workers):
            # each worker is a different thread
            worker = Worker(context, i, self.backend_addr)
            worker.start()
            workers.append(worker)

        # Setup proxy
        # This device (already implemented in ZMQ) connects the backend with the frontend
        zmq.proxy(frontend, backend)

        # join all the workers
        for w in workers:
            w.join()

        # close all the connections
        frontend.close()
        backend.close()
        context.term()


def main(args):
    restaurant = DriveThrough('tcp://' + str(args.ip) + ':' + str(args.port), args.n_workers)
    restaurant.start()
    restaurant.join()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Drive-through')
    parser.add_argument('--ip', type=ip_address, help='ip address', default='127.0.0.1')
    parser.add_argument('--port', type=check_port, help='ip port', default=5002)
    parser.add_argument('--n_workers', type=check_positive_number, help='number of workers', default=8)
    args = parser.parse_args()
    main(args)
