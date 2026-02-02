from cc3d.core.PySteppables import *
import numpy as np



class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self,frequency)

    def start(self):

        for cell in self.cell_list:
            if (cell.type>=3):
                cell.targetVolume = 64.0+10.0
                cell.lambdaVolume = 20.0
            else:
                cell.targetVolume=32.0
                cell.lambdaVolume=20.0
        
        
class GrowthSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def step(self, mcs):
        
        pt=CompuCell.Point3D()
        for cell in self.cell_list:
            if (cell.type==4): #Neovascular cells (NV)
                totalArea=0
                pt.x=int(round(cell.xCOM))
                pt.y=int(round(cell.yCOM))
                pt.z=int(round(cell.zCOM))
                VEGFconc=self.fieldL_VEGF.get(pt)
                cellNeighborList=self.getNeighborList(cell)
                for nsd in cellNeighborList:
                    if(nsd.neighborAddress and nsd.neighborAddress.type>=3):
                        totalArea+=nsd.commonSurfaceArea
                if (totalArea<45):
                    cell.targetVolume+=2.0*VEGFconc/(0.01+VEGFconc)
            if (cell.type==1): #Proliferating cells (P)
                pt.x=int(round(cell.xCOM))
                pt.y=int(round(cell.yCOM))
                pt.z=int(round(cell.zCOM))
                gluConc=self.fieldGLU.get(pt)
                #Proliferating cells become necrotic (N) when gluConc is low
                if (gluConc<0.001 and mcs>1000):
                    cell.type=2
                else:
                    cell.targetVolume+=0.022*gluConc/ (0.05+gluConc)
            if (cell.type==2): #Necrotic cells (N)
                cell.targetVolume-=0.1
                if cell.targetVolume<0.0:
                    cell.targetVolume=0.0

        
class MitosisSteppable(MitosisSteppableBase):
    def __init__(self,frequency=1):
        MitosisSteppableBase.__init__(self,frequency)

    def step(self, mcs):

        cells_to_divide=[]
        for cell in self.cell_list:
            if (cell.type==1 and cel.volume>64):
                cells_to_divide.apennd(cell)
            if (cell.type==4 and cell.volume>128):
                cells_to_divide.append(cell)

        for cell in cells_to_divide:
            self.divide_cell_random_orientation(cell)

    def update_attributes(self):
        parentCell=self.mitosisSteppable.parentCell
        childCell.targetVolume=parentCell.targetVolume/2
        parentCell.lambdaVolume=parentCell.targetVolume/2
        parentCell.lambdaVolume=parentCell.lambdaVolume
        childCell.type=parentCell.type
        childCell.targetVolume=parentCell.targetVolume
        childCell.lambdaVolume=parentCell.lambdaVolume

        
