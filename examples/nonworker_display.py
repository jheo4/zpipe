from zpipe.pipeline import Pipeline
from zpipe.stages.worker_stage import WorkerStage
from zpipe.stages.nonworker_stage import NonWorkerStage
from zpipe.utils.ztypes import *
from zpipe.utils.pickles import pickle_keypoints
import time
import cv2
import struct
import numpy as np
import copyreg

width = 1920
height = 1080

class CamSource():
    def init_class(self, cls_args):
        self.dev = cv2.VideoCapture(2)
        self.dev.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.dev.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def run(self, args):
        ret, frame = self.dev.read()
        #cv2.imshow("CamSource", frame)
        #if cv2.waitKey(1) & 0xFF == ord ('q'):
        #    return None
        #st = str(time.time()).encode()
        #return [frame, str(time.time()).encode()]
        print("st: ", time.time() * 1000)
        return [frame]

class KeyPoint():
    def init_class(self, cls_args):
        self.orb = cv2.ORB_create()
        copyreg.pickle(cv2.KeyPoint().__class__, pickle_keypoints)

    def run(self, args):
        frame = np.frombuffer(args[0][0], dtype=np.uint8).reshape(height, width, 3)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        rt = time.time()

        #print("Keypoint took: ", (rt - float(args[0][1]))*1000)

        return [keypoints, descriptors]

class Sink():
    def init_class(self, cls_args):
        pass

    def run(self, args):
        frame = np.frombuffer(args[0][0], dtype=np.uint8).reshape(height, width, 3)
        rt = time.time()
        #print("Sink received: ", (rt - float(args[0][1]))*1000)
        print("Sink received: ", rt)
        #print(args[1])

        cv2.imshow("Sink", frame)
        if cv2.waitKey(1) & 0xFF == ord ('q'):
            return None
        return None


test = Pipeline(port_base=10000, max_ports=100)

stage1 = NonWorkerStage()
stage2 = NonWorkerStage()
stage3 = NonWorkerStage()

stage1.init(CamSource, None, SRC, [None], BYTES)
stage2.init(KeyPoint, None, NOR, [BYTES], PYOBJ)
stage3.init(Sink, None, DST, [BYTES, PYOBJ], None)

test.add_stage(stage1)
test.add_stage(stage2)
test.add_stage(stage3)

test.link_stages(stage1, stage2, dependency=True, arg_pos=0, conflate=False)
test.link_stages(stage1, stage3, dependency=True, arg_pos=0, conflate=False)
test.link_stages(stage2, stage3, dependency=True, arg_pos=1, conflate=True)
test.start()