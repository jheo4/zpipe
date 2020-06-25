from pipeline import Pipeline
from stage import Stage
from worker import Worker
from vidgear.gears.camgear import CamGear
from ztypes import *
import cv2
import copyreg

def pickle_keypoints(point):
    return cv2.KeyPoint, (*point.pt, point.size, point.angle, point.response,
            point.octave, point.class_id)


class CamSource(Worker):
    def init_class(self, cls_args):
        dev_options = {'CAP_PROP_FRAME_WIDTH':cls_args['width'],
                       'CAP_PROP_FRAME_HEIGHT':cls_args['height'],
                       'CAP_PROP_FPS': cls_args['fps']}
        self.device = CamGear(source=cls_args['dev_idx'], **dev_options).start()
        self.orb = cv2.ORB_create()
        copyreg.pickle(cv2.KeyPoint().__class__, pickle_keypoints)

    def run_class(self, args):
        frame = self.device.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        return [keypoints, descriptors]
        #return frame

class Sink(Worker):
    def init_class(self, cls_args):
        pass

    def run_class(self, args):
        in_data = args[0]
        print(args)
        #cv2.imshow("args", in_data)
        #if cv2.waitKey(1) & 0xFF == ord ('q'):
        #    return None
        #return None

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