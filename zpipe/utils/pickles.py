import zlib, pickle
import copyreg

def send_zero_copy(socket, pyobj, protocol=-1):
    """
    send python object in zero-copy manner in zmq
        https://pyzmq.readthedocs.io/en/latest/api/zmq.html#zmq.Socket.send
        https://pyzmq.readthedocs.io/en/latest/serialization.html
    """
    pickled = pickle.dumps(pyobj, protocol)
    zipped_pickled = zlib.compress(pickled)
    return socket.send(zipped_pickled, copy=False)

def recv_zero_copy(socket, protocol=-1):
    """
    recv python object in zero-copy manner in zmq
        https://pyzmq.readthedocs.io/en/latest/api/zmq.html#zmq.Socket.send
        https://pyzmq.readthedocs.io/en/latest/serialization.html
    """
    zipped_pickled = socket.recv(copy=False)
    pickled = zlib.decompress(zipped_pickled)
    return pickle.loads(pickled)

import cv2
def pickle_keypoints(point):
    """
    pickle ocv keypoints; copyreg this function before sending ocv keypoints
        copyreg.pickle(cv2.KeyPoint().__class__, pickle_keypoints)
    """
    return cv2.KeyPoint, (*point.pt, point.size, point.angle, point.response,
                          point.octave, point.class_id)
