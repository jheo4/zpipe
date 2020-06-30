from zpipe.pipeline import Pipeline
from zpipe.stages.worker_stage import WorkerStage
from zpipe.worker import Worker
from zpipe.utils.ztypes import *
import cv2
import copyreg

def pickle_keypoints(point):
    return cv2.KeyPoint, (*point.pt, point.size, point.angle, point.response,
            point.octave, point.class_id)

class CamSource(Worker):
    def init_class(self, cls_args):
        self.dev = cv2.VideoCapture(cls_args['dev_idx'])
        width = cls_args['width']
        height = cls_args['height']
        self.dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.orb = cv2.ORB_create()
        copyreg.pickle(cv2.KeyPoint().__class__, pickle_keypoints)

    def run_class(self, args):
        _, frame = self.dev.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)

        return [keypoints, descriptors]


class Sink(Worker):
    def init_class(self, cls_args):
        pass

    def run_class(self, args):
        in_data = args[0]
        print(args)


class Sink(Worker):
    def init_class(self, cls_args):
        pass

    def run_class(self, args):
        in_data = args[0]
        print(args)


test = Pipeline(port_base=10000, max_ports=100)

stage1 = WorkerStage()
stage2 = WorkerStage()
stage3 = WorkerStage()
cam_source_args = {'width':1280, 'height':720, 'fps':30, 'dev_idx':2}
stage1.init(worker_cls=CamSource, worker_num=1, cls_args=cam_source_args, stage_type=SRC,
            itypes=[None], otype=PYOBJ)
stage2.init(worker_cls=Sink, worker_num=1, cls_args=None, stage_type=DST,
            itypes=[PYOBJ], otype='None')

test.add_stage(stage1)
test.add_stage(stage2)

test.link_stages(stage1, stage2, dependency=True, arg_pos=0, conflate=False)
test.start()
