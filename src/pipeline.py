from ztypes import *

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

        stage.worker_cls.make(stage.cls_args, stage.in_queue, stage.out_queue,
                              stage.worker_num, stage.stage_type)
        self.stages.append(stage)


    def link_stages(self, src, dest, dependency, arg_pos):
        if src.otype == dest.itype:
            dest.add_inlink(port=src.outlink_port, dependency=dependency, arg_pos=arg_pos)
        else:
            print("stage types are not matched")


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