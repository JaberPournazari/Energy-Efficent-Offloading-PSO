import numpy as np

from examples.PSO_Scheduling.Csa.CSA_proposed import TaskDeviceScheduler
from examples.PSO_Scheduling.comparing_orchestrator import comparing_orchestrator


class CsaProposedOrchestrator(comparing_orchestrator):
    """Very simple orchestrator that places the processing task on the fog node.

    You can try out other placements here and see how the placement may consume more energy ("cloud")
    or fail because there are not enough resources available ("sensor").
    """

    def __init__(self, infrastructure, applications, devices, tasks, alpha=.34, beta=.33, gamma=.33, delta=0,
                 num_particles=30, iterations=100, ap=0.02, fL=0.02, population_size=5):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure = infrastructure
        self.applications = applications
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.num_particles = num_particles
        self.iterations = iterations
        self.ap = ap
        self.fL = fL
        self.population_size = population_size
        self.legend = 'P-CSA'

        zeros = np.zeros(len(tasks), dtype=np.uint, order='C')
        ones = np.ones(len(tasks), dtype=np.uint, order='C')
        max_values = [i * (len(devices)-1) for i in ones]

        self.scheduler = TaskDeviceScheduler(self.devices, self.tasks, self.infrastructure, self.applications,
                                             alpha=self.alpha, beta=self.beta, gamma=self.gamma, delta=self.delta,
            population_size=population_size, ap=self.ap, fL=self.fL,
                                               min_values=zeros
                                               , max_values=max_values, iterations=self.iterations, verbose=False)

        super().__init__(infrastructure, applications, self.scheduler)
