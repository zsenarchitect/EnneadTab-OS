
try:
    from pyrevit import script
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass


import math

from EnneadTab import ENVIRONMENT, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_SELECTION, REVIT_VIEW, REVIT_UNIT

LIFE_SAFETY_CALCULATOR_FAMILY_NAME = "LifeSafetyCalculator"
LIFE_SAFETY_CALCULATOR_FAMILY_PATH = "{}\\REVIT\\{}.rvt".format(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT, LIFE_SAFETY_CALCULATOR_FAMILY_NAME)
LIFE_SAFETY_CALCULATOR_DUMP_VIEW = "EnneadTab_LifeSafetyCalculater"


class EgressData:
    data_collection = dict()

    @staticmethod
    def level_name_match(level_name):
        return level_name.replace(" Lachman/Wolman/Campus", "")\
                        .replace(" (also Wolman / Campus)", "")\
                        .replace(" Existing", "")\
                        .replace(" Lachman", "")\
                        .replace(" Existing", "")\
                        .replace(" Wolman / Campus Exist Roof", "")
    
    @classmethod
    def egress_id_exist(cls, test_id):
        for data in cls.data_collection.values():
            if data.egress_id == test_id:
                return True
        return False
    
    @property
    def is_stair(self):
        return "stair" in self.EgressId.lower()
    
    def __init__(self, level_name, egress_id):
        self.LevelName = level_name
        self.EgressId = egress_id

        self.RevitDoorObjCollection = []
        self.RevitStairObjCollection = []
        self.OccupancyLoad = 0

    @classmethod
    def get_data(cls, level_name, egress_id):
        level_name = EgressData.level_name_match(level_name)
        
        key = (level_name, egress_id)
        if key in cls.data_collection:
            return cls.data_collection[key]
        instance = EgressData(level_name, egress_id)
        cls.data_collection[key] = instance
        return instance


    def add_load(self, load):
        self.OccupancyLoad += load


    @property
    def TypeName(self):
        return "{}_{}".format(self.LevelName, self.EgressId)
    


    def __str__(self):
        return "Level: {}, Egress Id: {}, Occupancy Load: {}, Total Width: {}".format(self.LevelName, self.EgressId, self.OccupancyLoad, self.total_width)









class LifeSafetyChecker:

    @staticmethod
    def get_door_width(door, para_name):
        try:
            return door.LookupParameter(para_name).AsDouble()
        except:
            return door.Symbol.LookupParameter(para_name).AsDouble()



    @staticmethod
    def get_stair_width(stair):
        if not stair:
            return 
        runs = [stair.Document.GetElement(x) for x in stair.GetStairsRuns()]
        
        max_width = runs[0].ActualRunWidth
        for run in runs:
            if not  run.ActualRunWidth == max_width:
                print( "--This stair has variring  run width--->{}. Talk to Sen Zhang to understand what it means.".format(output.linkify(run.Id)))
        return max_width
    
    def __init__(self, doc, data_source):
        self.doc = doc
        self.data_source = data_source
        self.output = script.get_output()

        REVIT_FAMILY.get_family_by_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, 
                                         load_path_if_not_exist = LIFE_SAFETY_CALCULATOR_FAMILY_PATH)

    def run_check(self):
        # loop thru all spatial element, either from area or from room. 
        cate = DB.BuiltInCategory.OST_Rooms if self.data_source.Source == "Room" else DB.BuiltInCategory.OST_Areas
        all_spatial_elements = DB.FilteredElementCollector(self.doc).OfCategory(cate).WhereElementIsNotElementType().ToElements()

        if self.data_source.Source == "Area":
            all_spatial_elements = filter(lambda x: x.AreaScheme.Name == self.data_source.AreaSchemeName, all_spatial_elements)

        if len(all_spatial_elements) == 0:
            return

        # get a test spatial element to see if all needed parameter is valid
        tester = all_spatial_elements[0]
        if not self.varify_para_exist(tester):
            return
                          

        
        # for each egress data, 
            # collect final load number
            # find the target egress door and egress stair and egress exit of this spatial element, add to the load of that item data
        for spatial_element in all_spatial_elements:
            final_load = self.get_spatial_element_final_capacity(spatial_element)

            level_name = self.doc.GetElement(spatial_element.LevelId).Name
            target_list = self.get_spatial_element_target_list(spatial_element)

            # when a egress is assigned to A2+B2, the total load of this space need to divide to 2 parts and assign one each
            divider_count = len(target_list) 
            for target_name in target_list:
                local_load = int(math.ceil(final_load / float(divider_count)))
                target_data = EgressData.get_data(level_name, target_name)
                target_data.add_load(local_load)

            


        # for ground level need to treat specially: the immediate load(NOT the worst load) from above and below of EACH stair need to converge
        #  but do not need to add current ground level load to the same door


        self.gather_revit_objs()
        self.purge_bad_calculater()
        
        # for each item data, get a data calculator and update.
        # why not use revit obj directly? 
            # becasue stair can not easitl disply data by level. and stair and door if mixed in multi-category schdule can cause confusion, althoug it is technically possoble
            # because it is impossible to update door from a link
        for data_item in sorted(EgressData.data_collection.values(), key = lambda x: (x.LevelName, x.EgressId)):
            type_name = data_item.TypeName
            family_type = REVIT_FAMILY.get_family_type_by_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, type_name, create_if_not_exist=True)
            instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, type_name)

            if len(instances) == 0:
                instance = self.doc.Create.NewFamilyInstance(DB.XYZ(0, 0, 0), family_type, REVIT_VIEW.get_view_by_name(LIFE_SAFETY_CALCULATOR_DUMP_VIEW))
                instances = [instance]



            for doc in REVIT_APPLICATION.get_revit_link_docs(including_current_doc=True):
                level_obj = REVIT_SELECTION.get_level_by_name(data_item.LevelName, doc)
                if level_obj:
                    break
            else:
                print("Cannot find level obj [{}]".format(data_item.LevelName))
            data_item.LevelElevation = level_obj.Elevation



            door_width = 0
            for door in data_item.RevitDoorObjCollection:
                door_width += LifeSafetyChecker.get_door_width(door, self.data_source.ParaNameDoorWidth)
            data_item.EgressDoorWidth = door_width
            data_item.OccupancyDoorCapacity = int(math.floor(data_item.EgressDoorWidth * 12 /0.2))

            stair = data_item.RevitStairObjCollection[0] if len(data_item.RevitStairObjCollection) > 0 else None
            data_item.EgressStairWidth = LifeSafetyChecker.get_stair_width(stair) or family_type.LookupParameter("EgressStairWidth").AsDouble()
            data_item.OccupancyStairCapacity = int(math.floor(data_item.EgressStairWidth * 12 /0.3))

            if data_item.EgressId in ["Stair 1", "Stair 2", "Exit 1", "Exit 2"]:
                data_item.Zone = "New"
            else:
                data_item.Zone = "Existing"
                
            filler_para_names = [
                "EgressId",
                "LevelName",
                "LevelElevation",
                "EgressDoorWidth",
                "EgressStairWidth",
                "OccupancyDoorCapacity",
                "OccupancyStairCapacity",
                "OccupancyLoad",
                "Zone"
            ]
            for para_name in filler_para_names:
                family_type.LookupParameter(para_name).Set(getattr(data_item, para_name, 0))
            

    def gather_revit_objs(self):

        egress_id_para_name = self.data_source.ParaNameEgressId
        def is_valid_egress_id(element):
            if not element.LookupParameter(egress_id_para_name):
                return False
            if not element.LookupParameter(egress_id_para_name).HasValue:
                return False
            if not element.LookupParameter(egress_id_para_name).AsString() != "":
                return False
            return True

        for doc in REVIT_APPLICATION.get_revit_link_docs(including_current_doc=True):
            # print (doc.Title)
            all_doors = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements())
            all_doors = filter(is_valid_egress_id, all_doors)
            if (len(all_doors) == 0):
                # print("Cannot find any egress door in document <{}>".format(doc.Title))
                pass
            for door in all_doors:
                level_name = doc.GetElement(door.LevelId).Name
                egress_id = door.LookupParameter(egress_id_para_name).AsString()
                egress_data = EgressData.get_data(level_name, egress_id)
                egress_data.RevitDoorObjCollection.append(door)

            all_stairs = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements())
            all_stairs = filter(is_valid_egress_id, all_stairs)
            for stair in all_stairs:
                egress_id = stair.LookupParameter(egress_id_para_name).AsString()
                for item in EgressData.data_collection.items():
                    if item.EgressId == egress_id:
                        item.RevitStairObjCollection.append(stair)

                
    def varify_para_exist(self, tester):
        
        for para_name in [self.data_source.ParaNameLoadPerArea,
                          self.data_source.ParaNameLoadManual,
                          self.data_source.ParaNameTarget]:
            if tester.LookupParameter(para_name) is None:
                NOTIFICATION.messenger("Missing <{}> for the spatial element".format(para_name))
                return False

        return True

    
    def get_spatial_element_target_list(self, spatial_element):
        target_list = spatial_element.LookupParameter(self.data_source.ParaNameTarget).AsString()
        if target_list == "" or target_list is None:
            empty_target = "--No Egress Target--"
            print ("{}Egress target not assigned, please fix. Level = [{}]".format(self.output.linkify(spatial_element.Id, title = spatial_element.LookupParameter("Name").AsString()),
                                                                   spatial_element.Level.Name))
            spatial_element.LookupParameter(self.data_source.ParaNameTarget).Set(empty_target)
            return []
        
        if "+" in target_list:
            target_list = target_list.split("+")
            target_list = [x.strip() for x in target_list]
        else:
            target_list = [target_list]

        return target_list

    def get_spatial_element_final_capacity(self, spatial_element):

        # ignore rooms whose AreaPerPerson is negative
        if spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble() < 0:
            return 0
        
        # pioritise manual override
        if spatial_element.LookupParameter(self.data_source.ParaNameLoadManual).AsInteger() > 0:
            return spatial_element.LookupParameter(self.data_source.ParaNameLoadManual).AsInteger()
            

        return int(math.ceil(spatial_element.Area / spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble ()))


    def purge_bad_calculater(self):
        valid_type_names = [x.TypeName for x in EgressData.data_collection.values()]
   
        

        all_types = REVIT_FAMILY.get_all_types_by_family_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME)
        for type in all_types:
            if type.LookupParameter("Type Name").AsString() not in valid_type_names:
                self.doc.Delete(type.Id)
#####################################################################################################################################

class SpatialDataSource:
    """use this format to define how to extract lfe safety data, 
    each project mght want to do someting differently."""
    def __init__(self, source,
                 para_name_load_per_area,
                 para_name_load_manual,
                 para_name_target,
                 para_name_egress_id,
                 para_name_door_width,
                 area_scheme_name = None,
                 ):
        self.Source = source# "Area" or "Room"
        self.AreaSchemeName = area_scheme_name
        self.ParaNameLoadPerArea = para_name_load_per_area
        self.ParaNameLoadManual = para_name_load_manual
        self.ParaNameTarget = para_name_target
        self.ParaNameEgressId = para_name_egress_id
        self.ParaNameDoorWidth = para_name_door_width

def update_life_safety(doc, data_source):

    LifeSafetyChecker(doc, data_source).run_check()
    NOTIFICATION.messenger("Life Safety updated")
