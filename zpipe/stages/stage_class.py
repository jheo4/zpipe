from abc import ABCMeta, abstractmethod


class StageClass(metaclass=ABCMeta):
    @abstractmethod
    def init_class(self, cls_args):
        pass

    @abstractmethod
    def run(self, args):
        pass

