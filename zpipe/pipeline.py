from zpipe.utils.ztypes import *
from zpipe.stages.worker_stage import WorkerStage

class Pipeline():
    def __init__(self, port_base, max_ports):
        self.stages = []
        self.port_base = port_base
        self.max_ports = max_ports
        self.cur_ports = 0


    def add_stage(self, stage):
        if stage.stage_type is not DST:
            if self.cur_ports >= self.max_ports:
                print("Pipeline port is full")
                return
            stage.set_outlink(self.port_base + self.cur_ports)
            self.cur_ports+=1

        if stage.__class__ == WorkerStage:
            stage.worker_cls.make(stage.cls_args, stage.in_queue, stage.out_queue,
                                  stage.worker_num, stage.stage_type)
        self.stages.append(stage)


    def link_stages(self, src, dst, dependency, arg_pos):
        if src.stage_type is DST:
            print("dst cannot be the source of a linkage")
            return
        if dst.stage_type is SRC:
            print("src cannot be the destination of a linkage")
            return
        if src.otype not in dst.itypes:
            print("dst itypes don't include src otype")
            return
        if self.cur_ports >= self.max_ports:
            print("Pipeline link ports are full")
            return

        print("listen to ", src.outlink_port, " by ", dst.stage_type)
        dst.add_inlink(port=src.outlink_port, dependency=dependency, arg_pos=arg_pos)


    def start(self):
        for stage in self.stages:
            stage.start()


    def pause(self):
        for stage in self.stages:
            stage.pause()


    def stop(self):
        for stage in self.stages:
            stage.stop()

    def terminate(self):
        for stage in self.stages:
            stage.terminate()