from zpipe.pipeline import Pipeline
from zpipe.stages.nonworker_stage import NonWorkerStage
from zpipe.utils.ztypes import *
import time
import cv2
import numpy as np

width = 1920
height = 1080

class CamSource():
    def init_class(self, cls_args):
        self.dev = cv2.VideoCapture(cls_args['dev_idx'])
        self.dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def run(self, args):
        time.sleep(1)
        _, frame = self.dev.read()
        st = time.time()
        return [frame, st]


class Mid():
    def init_class(self, cls_args):
        pass

    def run(self, args):
        frame = np.frombuffer(args[0][0], dtype=np.uint8).reshape(height, width, 3)
        et = time.time() - float(args[0][1])
        print("Mid time: ", et * 1000)
        args[0][1] = time.time()
        return args[0]



class Sink():
    def init_class(self, cls_args):
        pass

    def run(self, args):
        et = time.time() - args[0][1]
        print("Sink time: ", et * 1000)
        print("------")
        return None


test = Pipeline(port_base=10000, max_ports=100)

stage1 = NonWorkerStage()
stage2 = NonWorkerStage()
stage3 = NonWorkerStage()
stage4 = NonWorkerStage()

cam_source_args = {'dev_idx':2}
stage1.init(stage_cls=CamSource, cls_args=cam_source_args, stage_type=SRC, itypes=[None], otype=PYOBJ)
stage2.init(stage_cls=Mid, cls_args={}, stage_type=NOR, itypes=[PYOBJ], otype=PYOBJ)
stage3.init(stage_cls=Mid, cls_args={}, stage_type=NOR, itypes=[PYOBJ], otype=PYOBJ)
stage4.init(stage_cls=Sink, cls_args={}, stage_type=DST, itypes=[PYOBJ], otype=None)

test.add_stage(stage1)
test.add_stage(stage2)
test.add_stage(stage3)
test.add_stage(stage4)

test.link_stages(stage1, stage2, dependency=True, arg_pos=0, conflate=False)
test.link_stages(stage2, stage3, dependency=True, arg_pos=0, conflate=False)
test.link_stages(stage3, stage4, dependency=True, arg_pos=0, conflate=False)
test.start()