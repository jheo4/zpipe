import zmq
import multiprocessing
from worker import Worker
from ztypes import *
import os, time


class Stage(multiprocessing.Process):
    def __del__(self):
        if self.outlink:
            self.outlink.close()


    def init(self, worker_cls=Worker, worker_num=1, cls_args=None, stage_type=NOR,
             itype=None, otype=None):
        # Workers
        self.worker_cls = worker_cls
        self.cls_args = cls_args
        self.worker_num = worker_num
        self.workers = []

        # Worker queue
        self.in_queue = multiprocessing.Queue()
        self.out_queue = multiprocessing.Queue()

        # Stage
        self.stage_type = stage_type
        self.itype = itype; self.otype = otype
        self.context = zmq.Context()
        self.outlink_port = None
        self.outlink = None
        if self.stage_type is not SRC:
            self.inlinks = {}
            self.inlink_info = {}
            self.inlink_poller = zmq.Poller()


    def run(self):
        self.build_outlink()
        self.build_inlinks()

        args = {}
        while True:
            if self.stage_type is not SRC:
                # inlinks with dependencies (blocking)
                for inlink, dep_and_pos in zip(self.inlinks.keys(), self.inlinks.values()):
                    if dep_and_pos[DEPENDENCY] is True:
                        args[dep_and_pos[POSITION]] = inlink.recv_pyobj()
                        print(type(args[dep_and_pos[POSITION]]))

                # inlinks without dependencies (nonblocking)
                ready_inlinks = dict(self.inlink_poller.poll(1))
                for inlink, dep_and_pos in zip(self.inlinks.keys(), self.inlinks.values()):
                    if inlink in ready_inlinks:
                        args[dep_and_pos[POSITION]] = inlink.recv_pyobj()
                self.in_queue.put(args)

            result = self.out_queue.get()
            #print("result for outlink ", result)

            if self.stage_type is not DST:
                self.outlink.send_pyobj(result)
            time.sleep(1)


    def set_outlink(self, port):
        """
        set outlink port to build the outlink in the subprocess
        """
        self.outlink_port = port


    def build_outlink(self):
        """
        build outlink socket as a publisher in the stage subprocess
        """
        if self.stage_type is not DST:
            self.outlink = self.context.socket(zmq.PUB)
            print(self.outlink_port)
            self.outlink.bind("tcp://*:" + str(self.outlink_port))


    def add_inlink(self, port, dependency=False, arg_pos=0):
        """
        add inlink dependency to build inlinks in the subprocess
        """
        if self.stage_type is SRC:
            print("src cannot not have inlink")
        else:
            self.inlink_info[port] = [dependency, arg_pos]


    def build_inlinks(self):
        """
        build inlink sockets (subscribers) in the stage subprocess
        """
        if self.stage_type is not SRC:
            for port, dep_and_pos in zip(self.inlink_info.keys(), self.inlink_info.values()):
                inlink = self.context.socket(zmq.SUB)
                inlink.setsockopt_string(zmq.SUBSCRIBE, '')
                inlink.setsockopt(zmq.CONFLATE, 1)
                inlink.connect("tcp://0.0.0.0:" + str(port))
                if dep_and_pos[DEPENDENCY] is False:
                    self.inlink_poller.register(inlink, zmq.POLLIN)
                self.inlinks[inlink] = dep_and_pos
