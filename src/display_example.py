from pipeline import Pipeline
from stage import Stage
from worker import Worker
from ztypes import *
import time
import cv2


class CamSource(Worker):
    def init_class(self, cls_args):
        self.dev = cv2.VideoCapture(2)

    def run_class(self, args):
        ret, frame = self.dev.read()
        cv2.imshow("CamSource", frame)
        if cv2.waitKey(1) & 0xFF == ord ('q'):
            return None
        return frame


class Sink(Worker):
    def init_class(self, cls_args):
        pass

    def run_class(self, args):
        print("Sink received: ", args[0])
        in_data = args[0]
        cv2.imshow("Sink", in_data)
        if cv2.waitKey(1) & 0xFF == ord ('q'):
            return None
        return None


test = Pipeline(port_base=10000, max_ports=100)

stage1 = Stage()
stage2 = Stage()
cam_source_args = {'width':1280, 'height':720, 'fps':30, 'dev_idx':2}
stage1.init(worker_cls=CamSource, worker_num=1, cls_args=cam_source_args, stage_type=SRC,
            itype=None, otype='FRAME')
stage2.init(worker_cls=Sink, worker_num=1, cls_args=None, stage_type=DST,
            itype='FRAME', otype='None')

test.add_stage(stage1)
test.add_stage(stage2)

test.link_stages(stage1, stage2, dependency=True, arg_pos=0)
test.start()