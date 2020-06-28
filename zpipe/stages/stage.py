import multiprocessing
from abc import ABCMeta, abstractmethod


class Stage(multiprocessing.Process, metaclass=ABCMeta):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

    def shutdown(self):
        print ("Shutdown initiated")
        self.exit.set()

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def set_outlink(self):
        pass

    @abstractmethod
    def build_outlink(self):
        pass

    @abstractmethod
    def add_inlink(self):
        pass

    @abstractmethod
    def build_inlinks(self):
        pass