from zpipe.pipeline import Pipeline
from zpipe.stages.worker_stage import WorkerStage
from zpipe.worker import Worker
from zpipe.utils.ztypes import *
import time
import cv2


class CamSource(Worker):
    def init_class(self, cls_args):
        self.dev = cv2.VideoCapture(2)
        width = 1920
        height = 1080
        self.dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        _, self.frame = self.dev.read()

    def run_class(self, args):
        time.sleep(1)
        st = time.time()
        return [self.frame, st]


class Mid(Worker):
    def init_class(self, cls_args):
        pass

    def run_class(self, args):
        et = time.time() - args[0][1]
        print("propagation time: ", et * 1000)
        args[0][1] = time.time()
        return args[0]



class Sink(Worker):
    def init_class(self, cls_args):
        pass

    def run_class(self, args):
        et = time.time() - args[0][1]
        print("propagation time: ", et * 1000)
        print("------")
        return None


test = Pipeline(port_base=10000, max_ports=100)

stage1 = WorkerStage()
stage2 = WorkerStage()
stage3 = WorkerStage()
stage4 = WorkerStage()

cam_source_args = {'width':1280, 'height':720, 'fps':30, 'dev_idx':2}
stage1.init(worker_cls=CamSource, worker_num=1, cls_args=cam_source_args, stage_type=SRC,
            itypes=[None], otype='FRAME')
stage2.init(worker_cls=Mid, worker_num=1, cls_args=None, stage_type=NOR,
            itypes=['FRAME'], otype='FRAME')
stage3.init(worker_cls=Mid, worker_num=1, cls_args=None, stage_type=NOR,
            itypes=['FRAME'], otype='FRAME')
stage4.init(worker_cls=Sink, worker_num=1, cls_args=None, stage_type=DST,
            itypes=['FRAME'], otype='None')

test.add_stage(stage1)
test.add_stage(stage2)
test.add_stage(stage3)
test.add_stage(stage4)

test.link_stages(stage1, stage2, dependency=True, arg_pos=0)
test.link_stages(stage2, stage3, dependency=True, arg_pos=0)
test.link_stages(stage3, stage4, dependency=True, arg_pos=0)
test.start()