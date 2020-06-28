import multiprocessing
from zpipe.utils.ztypes import *
import os, time


class Worker(multiprocessing.Process):
    @classmethod
    def make(cls, cls_args, in_queue, out_queue, num_workers, stage_type):
        workers = []
        for idx in range(num_workers):
            worker = cls()
            worker.init_queues(in_queue, out_queue, stage_type)
            worker.init_class(cls_args)
            workers.append(worker)

        for worker in workers:
            worker.start()


    def run(self):
        while True:
            in_args = None
            if self.stage_type is not SRC:
                in_args = self.in_queue.get()
            out_res = self.run_class(in_args)
            self.out_queue.put(out_res)


    def init_queues(self, in_queue, out_queue, stage_type):
        self.stage_type = stage_type
        self.in_queue = in_queue
        self.out_queue = out_queue


    def init_class(self, args):
        pass


    def run_class(self, args):
        pass