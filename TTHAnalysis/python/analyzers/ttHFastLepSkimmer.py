from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
import itertools

class ttHFastLepSkimmer( Analyzer ):
    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(ttHFastLepSkimmer,self).__init__(cfg_ana,cfg_comp,looperName)
        self.muIdCut = self.cfg_ana.muCut
        self.eleIdCut = self.cfg_ana.eleCut
        self.requireSameSignPair = getattr(cfg_ana,"requireSameSignPair",False)
        self.ptCuts = getattr(cfg_ana,"ptCuts",[])

    def declareHandles(self):
        super(ttHFastLepSkimmer, self).declareHandles()
        self.handles['muons'] = AutoHandle(self.cfg_ana.muons,"std::vector<pat::Muon>")            
        self.handles['electrons'] = AutoHandle(self.cfg_ana.electrons,"std::vector<pat::Electron>")            

    def beginLoop(self, setup):
        super(ttHFastLepSkimmer,self).beginLoop(setup)
        self.counters.addCounter('events')
        self.count = self.counters.counter('events')
        self.count.register('all events')
        self.count.register('accepted events')


    def process(self, event):
        self.readCollections( event.input )
        self.count.inc('all events')
        
        leptons = 0
        charges = []
        pts     = []

        for el in self.handles['electrons'].product():
            if self.eleIdCut(el): 
                charges.append(el.charge())
                pts.append(el.pt())
                leptons += 1

        for mu in self.handles['muons'].product():
            if self.muIdCut(mu): 
                charges.append(mu.charge())
                pts.append(mu.pt())
                leptons += 1

        pts.sort(reverse = True)
        if leptons >= self.cfg_ana.minLeptons:
             if len(self.ptCuts):
                for ptLep,cutValue in zip(pts,self.ptCuts):
                    if ptLep < cutValue:
                        return False
             self.count.inc('accepted events')
             if self.requireSameSignPair:
                 return any([(q1 == q2) for q1,q2 in itertools.combinations(charges,2)])
             else:
                 return True

        return False
