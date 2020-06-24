import zmq
import multiprocessing
from ztypes import *
import os, time

class Stage(multiprocessing.Process):
    def __del__(self):
        if self.outlink:
            self.outlink.close()

    def init(self, worker_cls, worker_num, cls_args, is_src=False):
        # Workers
        self.worker_cls = worker_cls
        self.cls_args = cls_args
        self.worker_num = worker_num
        self.workers = []

        # Worker link
        self.in_queue = multiprocessing.Queue()
        self.out_queue = multiprocessing.Queue()

        # Stage links
        self.is_src = is_src
        self.context = zmq.Context()
        self.outlink_port = None
        self.outlink = None
        if self.is_src is False:
            self.inlinks = {}
            self.inlink_info = {}
            self.inlink_poller = zmq.Poller()

    def run(self):
        self.build_outlink()
        self.build_inlinks()
        while True:
            """
            print(f"[Stage {self.cls_args}] run ", self.worker_cls, self.cls_args)
            args = {}
            # inlinks with dependencies (blocking)
            ready_inlinks = dict(self.inlink_poller.poll(1))
            for inlink, dep_and_tag in zip(self.inlinks.keys(), self.inlinks.values()):
                if dep_and_tag[DEPENDENCY] is True:
                    print(f"[Stage {self.cls_args}] DEPENDENCY")
                    print(inlink)
                    args[dep_and_tag[ARG_TAG]] = inlink.recv()

            # inlinks without dependencies (nonblocking)
            ready_inlinks = dict(self.inlink_poller.poll(1))
            for inlink, dep_and_tag in zip(self.inlinks.keys(), self.inlinks.values()):
                if inlink in ready_inlinks:
                    args[dep_and_tag[ARG_TAG]] = inlink.recv()

            self.in_queue.put(args)
            result = self.out_queue.get()
            print(f"[Stage {self.cls_args}] outlink.send: ", result)
            if result is not None:
                self.outlink.send("abcd".encode())
            """
            if self.is_src:
                print("[send from src! ", self.outlink, "]")
                self.outlink.send("This is from source!".encode())
            else:
                in_data = self.inlink.recv()
                print("[recv from src]: ", in_data)
                self.outlink.send("Received from source".encode())

            time.sleep(1)

    def set_outlink(self, port):
        self.outlink_port = port

    def build_outlink(self):
        """
        create outlink socket as a publisher
        """
        self.outlink = self.context.socket(zmq.PUB)
        self.outlink.bind("tcp://*:" + str(self.outlink_port))

    def add_inlink(self, port, dependency=False, arg_tag=None):
        """
        add inlink to a stage with dependency
        """
        if self.is_src is False:
            self.inlink_info[port] = [dependency, arg_tag]
        else:
            print("src cannot not have inlink")

    def build_inlinks(self):
        if self.is_src is False:
            for port, dep_and_tag in zip(self.inlink_info.keys(), self.inlink_info.values()):
                self.inlink = self.context.socket(zmq.SUB)
                self.inlink.setsockopt_string(zmq.SUBSCRIBE, '')
                self.inlink.setsockopt(zmq.CONFLATE, 1)
                self.inlink.connect("tcp://0.0.0.0:" + str(port))
                if dep_and_tag[DEPENDENCY] is False:
                    self.inlink_poller.register(self.inlink, zmq.POLLIN)
                #self.inlinks[inlink] = [dependency, arg_tag]
