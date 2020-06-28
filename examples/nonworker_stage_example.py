from zpipe.pipeline import Pipeline
from zpipe.stages.nonworker_stage import NonWorkerStage
from zpipe.utils.ztypes import *
from vidgear.gears import CamGear
import time

class CamSource():
    def init_class(self, cls_args):
        #self.dev = cv2.VideoCapture(2)

        dev_options = {'CAP_PROP_FRAME_WIDTH':1920,
                       'CAP_PROP_FRAME_HEIGHT':1080,
                       'CAP_PROP_FPS': 30}
        self.dev = CamGear(source=2, **dev_options)
        self.dev.start()
        #width = 1920
        #height = 1080
        #self.dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        #self.dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        #self.data = b'x' * 1920 * 1080 * 3

    def run(self, args):
        time.sleep(0.032)
        self.frame = self.dev.read()
        return [self.frame, time.time()]
        #return b'x' * 100


class Mid():
    def init_class(self, cls_args):
        pass

    def run(self, args):
        #print("Sink received: ", len(args[0]), type(args[0]))
        a = args[0]
        #print(a[0].shape)
        #print(a[1])
        print("mid recv: ", (time.time() - a[1]) * 1000)
        return [a[0], time.time()]


class Sink():
    def init_class(self, cls_args):
        pass

    def run(self, args):
        #print("Sink received: ", len(args[0]), type(args[0]))
        a = args[0]
        #a1 = args[1]
        #b = a[0]
        #b[0][0][0] = 55
        print("dst recv from s2: ", (time.time() - a[1]) * 1000)
        #print("dst recv from s22: ", (time.time() - a1[1]) * 1000)
        print("")
        return None


test = Pipeline(port_base=10000, max_ports=100)

stage1 = NonWorkerStage()
stage2 = NonWorkerStage()
stage22 = NonWorkerStage()
stage3 = NonWorkerStage()
cam_source_args = {'width':1280, 'height':720, 'fps':30, 'dev_idx':2}
stage1.init(stage_cls=CamSource, cls_args=cam_source_args, stage_type=SRC,
            itypes=[None], otype='FRAME')
stage2.init(stage_cls=Mid, cls_args=None, stage_type=NOR,
            itypes=['FRAME'], otype='FRAME')
stage22.init(stage_cls=Mid, cls_args=None, stage_type=NOR,
            itypes=['FRAME'], otype='FRAME')
stage3.init(stage_cls=Sink, cls_args=None, stage_type=DST,
            itypes=['FRAME'], otype='None')

test.add_stage(stage1)
test.add_stage(stage2)
test.add_stage(stage22)
test.add_stage(stage3)

test.link_stages(stage1, stage2, dependency=True, arg_pos=0)
test.link_stages(stage1, stage22, dependency=True, arg_pos=0)
test.link_stages(stage2, stage3, dependency=True, arg_pos=0)
test.link_stages(stage22, stage3, dependency=True, arg_pos=1)
test.start()