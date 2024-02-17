import os
from typing import List
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse   
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NOC_WHITE,
)
from OCC.Display.SimpleGui import init_display


class STPFileReader:
    @classmethod  
    def read_stp_file_by_occ(cls, file_name:str) -> TopoDS_Compound:
        step_reader = STEPControl_Reader()
        step_reader.ReadFile(file_name)
        step_reader.TransferRoots()  
        
        return step_reader.Shape()

class UI:
    def __init__(self) -> None:
        self.pos_pnt: List[gp_Pnt] = [(0,0,0), (0, 100, 100)]
        self.file_path_list: List[str] = []
        self.brep_shape_list: List[TopoDS_Compound] = []   
        self.display_occ_object_list: List[DisplayObject] = [] 
    

    def get_brep_models(self) -> None:
        current_directory = os.getcwd()
        all_files_and_dirs = os.listdir(current_directory)

        for item in all_files_and_dirs:
            file_path = os.path.join(current_directory, item)
            
            if os.path.isfile(file_path):
                base_name, extension = os.path.splitext(file_path)
                if extension == '.stp' or extension == '.STEP':
                    self.file_path_list.append(file_path)
                    
        for idx, file_path in enumerate(self.file_path_list):
            brep_shape = STPFileReader.read_stp_file_by_occ(file_path)
            translation = gp_Trsf()
            
            translation.SetTranslation(gp_Vec(*self.pos_pnt[idx]))
            transformed_shape: TopoDS_Compound =\
                BRepBuilderAPI_Transform(brep_shape, translation, True).Shape()
            self.brep_shape_list.append(transformed_shape)
            self.display_occ_object_list.append(
                DisplayObject(occ_object=transformed_shape,
                            transparency=0)
            )
        
            
    def display_occ_objects(self) -> None:
        display, start_display, _, _ = init_display()
        display.View.SetBgGradientColors(
        Quantity_Color(Quantity_NOC_WHITE),
        Quantity_Color(Quantity_NOC_WHITE),
        2,
        True)
        
        for display_object in self.display_occ_object_list:
            display.DisplayShape(display_object.occ_object,
                                color=display_object.color,
                                transparency=display_object.transparency)
        display.DisplayShape(gp_Pnt(0, 0, 0), color="red", update=True)
        start_display()

class DisplayObject:
    def __init__(self, 
                occ_object: object,
                transparency: float = 0,
                color: str = "blue") -> None:
        self.occ_object = occ_object
        self.transparency: float = transparency
        self.color: str = color

class Document:
    def __init__(self, ui: UI) -> None:
        self.ui: UI = ui    
    
    
    def get_brep_models(self) -> List[TopoDS_Compound]:
        return self.ui.brep_shape_list
    
    def get_fused_brep_model(self) -> TopoDS_Compound:
        fused_shape = self.ui.brep_shape_list[0]    
        
        if len(self.ui.brep_shape_list) == 1:
            return fused_shape  
        
        for shape in self.ui.brep_shape_list[1:]:
            fused_shape = BRepAlgoAPI_Fuse(fused_shape, shape).Shape()  
        return fused_shape  
        
    def set_display_object(self, 
                        object: object, 
                        color:str = "blue", 
                        transparency:float = 0) -> None:
        self.ui.display_occ_object_list.append(DisplayObject(
            occ_object=object,
            transparency=transparency,
            color=color
        ))
        return
    
    def display(self) -> None:
        self.ui.display_occ_objects()

ui = UI()
ui.get_brep_models()
document = Document(ui)