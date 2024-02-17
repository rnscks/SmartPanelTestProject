from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox    
from OCC.Display.SimpleGui import init_display

from typing import List

corner_min = gp_Pnt(0, 0, 0)    
corner_max = gp_Pnt(10, 10, 10) 
resoloution: int = 4 
gap: float = (corner_max.X() - corner_min.X())/resoloution
x,y,z = corner_min.X(), corner_min.Y(), corner_min.Z()  

pnt_list: List[gp_Pnt] = []

for i in range(resoloution + 1):
    for j in range(resoloution + 1):
        for k in range(resoloution + 1):
            nx: float = x + i * gap
            ny: float = y + j * gap
            nz: float = z + k * gap
            
            pnt_list.append(gp_Pnt(nx, ny, nz))

display, start_display, _, _ = init_display()
box_shape = BRepPrimAPI_MakeBox(corner_min, corner_max).Shape()
display.DisplayShape(box_shape, transparency=0.8)
for pnt in pnt_list:
    display.DisplayShape(pnt)   
start_display() 