from examples.PSO_Scheduling.Pso.PSO import TaskDeviceScheduler
from examples.PSO_Scheduling.comparing_orchestrator import comparing_orchestrator


class PSOOrchestrator(comparing_orchestrator):
    """Very simple orchestrator that places the processing task on the fog node.

    You can try out other placements here and see how the placement may consume more energy ("cloud")
    or fail because there are not enough resources available ("sensor").
    """

    def  __init__ (self,infrastructure,applications,devices,tasks,alpha=25,beta=25,gamma=25,delta=25,
                   num_particles=30, max_iter=100, c1=1.5, c2=1.5,
                 w=0.9, w_damp=0.99):
        self.devices=devices
        self.tasks=tasks
        self.infrastructure=infrastructure
        self.applications=applications
        self.alpha=alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.num_particles=num_particles
        self.max_iter=max_iter
        self.c1=c1
        self.c2=c2
        self.w=w
        self.w_damp=w_damp
        self.legend='B-PSO'


        self.scheduler=TaskDeviceScheduler(self.devices, self.tasks, self.infrastructure, self.applications,
                                           num_particles=self.num_particles,max_iter=self.max_iter,c1=self.c1,
                                           c2=self.c2,w= self.w,w_damp=self.w_damp)

        super().__init__(infrastructure, applications, self.scheduler)




