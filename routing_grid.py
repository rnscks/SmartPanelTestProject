from typing import List, Optional   
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier

from brep_controller import document, Document


class Box:
    def __init__(self, corner_max: gp_Pnt, corner_min: gp_Pnt) -> None:
        self.corner_min: gp_Pnt = corner_min
        self.corner_max: gp_Pnt = corner_max
        
        center_x: float = (corner_max.X() + corner_min.X())/2   
        center_y: float = (corner_max.Y() + corner_min.Y())/2
        center_z: float = (corner_max.Z() + corner_min.Z())/2
        
        self.center_pnt: gp_Pnt = gp_Pnt(center_x, center_y, center_z)
        self.box_shape = BRepPrimAPI_MakeBox(corner_min, corner_max).Shape()
        
    def set_display_object_by_document(self, document: Document) -> None:
        document.set_display_object(self.box_shape, transparency=0.5)
        return  

class Node(Box):
    def __init__(self,corner_max: gp_Pnt, corner_min: gp_Pnt, i: int = 0, j: int = 0, k: int = 0) -> None:
        super().__init__(corner_max, corner_min)    
        self.i: int = i
        self.j: int = j
        self.k: int = k
        self.is_obstacle: bool = True

class RoutingGrid:
    def __init__(self, fused_shape: TopoDS_Shape, extension_ratio: float = 0.3, dim: int = 10) -> None:
        self.dim: int  = dim
        self.fused_shape = fused_shape
        self.bnd_box = Bnd_Box() 
        self.grids: List[List[List[Optional[Node]]]] =\
            [[[None for _ in range(self.dim)] for _ in range(self.dim)] for _ in range(self.dim)]   
        
        classifier = BRepClass3d_SolidClassifier() 
        classifier.Load(fused_shape)

        self.initialize_extensioned_bnd_box(extension_ratio)
        self.initialize_node_in_grid()

        
    def initialize_extensioned_bnd_box(self, enxtension_ratio: float = 0.2) -> None:
        brepbndlib.Add(self.fused_shape
                        ,self.bnd_box)
        corner_min, corner_max = self.bnd_box.CornerMin(), self.bnd_box.CornerMax()
        extended_length: float = corner_max.Distance(corner_min) * enxtension_ratio 
        self.bnd_box.SetGap(extended_length)
        extended_corner_min = self.bnd_box.CornerMin()
        extended_corner_max = self.bnd_box.CornerMax()
        
        
        max_length: float = max(abs(extended_corner_max.X() - extended_corner_min.X()), 
                                abs(extended_corner_max.Y() - extended_corner_min.Y()),
                                abs(extended_corner_max.Z() - extended_corner_min.Z()))
        extended_corner_min.SetX(extended_corner_max.X() - max_length) 
        extended_corner_min.SetY(extended_corner_max.Y() - max_length) 
        extended_corner_min.SetZ(extended_corner_max.Z() - max_length) 
        
        self.bnd_box = Bnd_Box(extended_corner_min, extended_corner_max)    
        return 
        
    def initialize_node_in_grid(self):
        gap: float =\
            (self.bnd_box.CornerMax().X() - self.bnd_box.CornerMin().X()) / self.dim 

        for i in range(self.dim):
            for j in range(self.dim):
                for k in range(self.dim):
                    corner_min = gp_Pnt(self.bnd_box.CornerMin().X() + i * gap,
                                        self.bnd_box.CornerMin().Y() + j * gap,
                                        self.bnd_box.CornerMin().Z() + k * gap)
                    corner_max = gp_Pnt(self.bnd_box.CornerMin().X() + (i+1) * gap,
                                        self.bnd_box.CornerMin().Y() + (j+1) * gap,
                                        self.bnd_box.CornerMin().Z() + (k+1) * gap)
                    node = Node(corner_max, corner_min, i, j, k)
                    self.grids[i][j][k] = node      
        return
    
    def set_display_object_by_document(self, document: Document) -> None:   
        for node in self:
            if node.is_obstacle:
                document.set_display_object(node.box_shape, transparency=1)
        return  
    
    def __iter__(self):
        for i in range(self.dim):
            for j in range(self.dim):
                for k in range(self.dim):
                    yield self.grids[i][j][k]
        return  
    
    def __getitem__(self, index: tuple):
        i, j, k = index
        return self.grids[i][j][k]

if __name__ == "__main__":
    # domain layer
    fused_brep_model = document.get_fused_brep_model()
    
    routing_grid = RoutingGrid(fused_brep_model) 
    bnd_box = routing_grid.bnd_box
    box = Box(
        corner_max=bnd_box.CornerMax(),
        corner_min=bnd_box.CornerMin())    
    
    box.set_display_object_by_document(document)
    routing_grid.set_display_object_by_document(document)   
    document.display()
