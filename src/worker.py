import multiprocessing
import os, time

class Worker(multiprocessing.Process):
    @classmethod
    def make(cls, args, in_queue, out_queue, num_workers):
        workers = []
        for idx in range(num_workers):
            worker = cls()
            worker.init_queues(in_queue, out_queue)
            worker.init_class(args)
            workers.append(worker)

        for worker in workers:
            worker.start()

    def run(self):
        while True:
            print(f"[WORKER {self.args}] get inqueue")
            in_args = self.in_queue.get()
            print(f"[WORKER {self.args}] do_task")
            out_res = self.do_task(in_args)
            print(f"[WORKER {self.args}] put outqueue: ", out_res)
            self.out_queue.put(out_res)


    def init_queues(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue

    def init_class(self, args):
        pass

    def do_task(self, args):
        pass