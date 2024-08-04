import ENVIRONMENT



class DataType:
    ElementId = "ElementId"
    Curve = "Curve"
    CurveLoop = "CurveLoop"
    Point3d = "Point3d"
    TableCellCombinedParameterData = "TableCellCombinedParameterData"
    XYZ = "XYZ"
    Double = "Double"


def list_to_system_list(list, type = DataType.ElementId, use_IList = False):
    """convert python list to System collection List. 
    In many occasions there need a cast to get to a more strong type of List object

    Args:
        list (python list): _description_
        type (str, optional): the description for target data type. Defaults to "ElementId".
        use_IList (bool, optional): _description_. Defaults to False.

    Returns:
        System.Collections.Generic.List: _description_
    """

    import System # pyright: ignore
    if ENVIRONMENT.is_Revit_environment():
        from Autodesk.Revit import DB # pyright: ignore
    if ENVIRONMENT.is_Rhino_environment():
        import Rhino # pyright: ignore

    if use_IList:
        if type == DataType.CurveLoop:
            return System.Collections.Generic.IList[DB.CurveLoop](list)

        if type == DataType.TableCellCombinedParameterData:
            return System.Collections.Generic.IList[DB.TableCellCombinedParameterData](list)






        return System.Collections.Generic.IList[type](list)


    if type == DataType.Point3d:
        return System.Collections.Generic.List[Rhino.Geometry.Point3d](list)
    if type == DataType.ElementId:
        return System.Collections.Generic.List[DB.ElementId](list)
    if type == DataType.CurveLoop:
        return System.Collections.Generic.List[DB.CurveLoop](list)
    if type == DataType.Curve:
        return System.Collections.Generic.List[DB.Curve](list)
    if type == DataType.TableCellCombinedParameterData:
        return System.Collections.Generic.List[DB.TableCellCombinedParameterData](list)


    if type == DataType.XYZ:
        pts = System.Collections.Generic.List[DB.XYZ]()
        for pt in list:
            pts.Add(pt)
        return pts

    if type == DataType.Double:
        values = System.Collections.Generic.List[System.Double]()
        for value in list:
            values.Add(value)
          
        return values

    return System.Collections.Generic.List[type](list)
    #print_note("Things are not right here...type = {}".format(type))

    return False

def compare_list(A, B):
    unique_A = [x for x in A if x not in B]
    unique_B = [x for x in B if x not in A]
    shared = [x for x in A if x in B]


def unit_test():
    # print all the enumerate of DataType
    print ("All DataType in class:")
    for i, type in enumerate(dir(DataType)):
        if type.startswith("__"):
            continue
        print("{}: {}".format(type, getattr(DataType, type)))
    pass