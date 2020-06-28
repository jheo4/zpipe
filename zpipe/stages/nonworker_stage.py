import zmq
import multiprocessing
from zpipe.worker import Worker
from zpipe.stages.stage import Stage
from zpipe.utils.ztypes import *
from threading import Thread
import os, time


class NonWorkerStage(Stage):
    def __del__(self):
        for outlink in self.outlinks:
            if outlink:
                self.outlink.close()


    def init(self, stage_cls=None, cls_args=None, stage_type=NOR,
             itypes=[None], otype=None):
        # Workers
        self.stage_cls = stage_cls()
        self.cls_args = cls_args

        # Stage
        self.context = zmq.Context()
        self.stage_type = stage_type
        self.itypes = itypes; self.otype = otype

        self.outlinks = []
        self.outlink_ports = []

        self.inlinks = {}
        self.inlink_info = {}
        self.inlink_poller = zmq.Poller()


    def run(self):
        """
        run stage class wint input arguments from inlinks and put the results
        into outlinks
        """
        self.stage_cls.init_class(self.cls_args)
        self.build_outlink()
        self.build_inlinks()

        args = {}
        while not self.exit.is_set():
            # read inlinks
            if self.stage_type is not SRC:
                # inlinks with dependencies (blocking)
                for inlink, dep_and_pos in zip(self.inlinks.keys(), self.inlinks.values()):
                    if dep_and_pos[DEPENDENCY] is True:
                        args[dep_and_pos[POSITION]] = inlink.recv_pyobj()

                # inlinks without dependencies (nonblocking)
                ready_inlinks = dict(self.inlink_poller.poll(1))
                for inlink, dep_and_pos in zip(self.inlinks.keys(), self.inlinks.values()):
                    if inlink in ready_inlinks:
                        args[dep_and_pos[POSITION]] = inlink.recv_pyobj()

            # run class functionality
            #st = time.time()
            result = self.stage_cls.run(args)
            #et = (time.time() - st) * 1000
            #print(f"{self.stage_cls} took: ", et)


            # put the output to outputlinks
            if self.stage_type is not DST:
                print("frame start from src!")
                self.outlink.send_pyobj(result)


    def set_outlink(self, port):
        """
        set outlink port to build the outlink in the subprocess
        """
        self.outlink_port = port
        print("set outlink ", port, " of ", self.stage_type)


    def build_outlink(self):
        """
        build outlink socket as a publisher in the stage subprocess
        """
        if self.stage_type is not DST:
            self.outlink = self.context.socket(zmq.PUB)
            self.outlink.bind("tcp://0.0.0.0:" + str(self.outlink_port))
            print("build outlink tcp://0.0.0.0:" + str(self.outlink_port), " by ", self.stage_type)


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
                print("build inlinks tcp://0.0.0.0:" + str(port), " by ", self.stage_type)
                if dep_and_pos[DEPENDENCY] is False:
                    self.inlink_poller.register(inlink, zmq.POLLIN)
                self.inlinks[inlink] = dep_and_pos
