"""used to create, store and retreiave schema data that can travel with revit doc instead of L drive external storage.
This idea is very helpful becasue it remove many proejct data storage dependecy to server.

This also means there is no need to create temperory shared parameter for some script and bind to categpry. 
However, this will also mean the info is not visiable to user, so no luck seeing then in schedule or have it controled by user.
ONLY USE IT WHEN THE CONTENT IS NEVER EXPECTED TO BE MODIFIED THRU UI."""



"""https://twentytwo.space/2021/02/27/revit-api-extensible-storage-schema/
this a helpful guide on how to use schema. Good examples




https://help.autodesk.com/view/RVT/2024/ENU/?guid=Revit_API_Revit_API_Developers_Guide_Advanced_Topics_Storing_Data_in_the_Revit_model_Extensible_Storage_html
this is the help guide from official Autodesk, aslo good




https://archi-lab.net/what-why-and-how-of-the-extensible-storage/
one more from Archi-lab, should read this FIRST!!!!!!!!!!!!!!!!!!!!!!!!!"""


try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    from System import Guid, String

except:
    pass


STABLE_SCHEMA_DATAS = [
    {
    "name": "SampleSchema1",
    "description": "Sample doc for the sample schema",
    "guid": "0DC954AE-ADEF-41c1-8D38-EB5B8225D255",
    "fields":[("testboolean", bool),
              ("teststring", str),
              ("testfloat", float),
              ("testint", int)]
    },
    {
    "name": "SampleSchema2",
    "description": "Another sample doc for the sample schema",
    "guid": "0DC954AE-ADEF-41c1-8D38-EB5B8115D235",
    "fields":[
              ("testint", int)]
    }
                       ]

def get_schema_by_name(schema_name):
    schemas = DB.ExtensibleStorage.Schema.ListSchemas()
    for schema in schemas:
        if schema.SchemaName == schema_name:
            return schema
    return None

def create_schema(schema_name):

    for stable_data in STABLE_SCHEMA_DATAS:
        if stable_data.get("name") == schema_name:
            stable_schema_data = stable_data
            break
    else:
        raise ValueError("No stable schema data found for the schema name: {}".format(schema_name))
  
    schema_name, schema_description = stable_schema_data.get("name"), stable_schema_data.get("description")
    guid = Guid(stable_schema_data.get("guid"))

    schema_builder = DB.ExtensibleStorage.SchemaBuilder(guid)

    schema_builder.SetReadAccessLevel(DB.ExtensibleStorage.AccessLevel.Public) #.Application
    schema_builder.SetWriteAccessLevel(DB.ExtensibleStorage.AccessLevel.Vendor)
    schema_builder.SetVendorId("EnneadTab")

    schema_builder.SetSchemaName(schema_name)
    schema_builder.SetDocumentation(schema_description)

    for item in stable_schema_data.get("fields"):
        field_name, field_type = item
        print (field_name, field_type)
        if not schema_builder.AcceptableName (field_name):
            raise ValueError("Field name is not acceptable: {}\n The allowable characters are ASCII letters, numbers (except the first character) and underscore. The length must be between 1 and 247 characters.".format(field_name))
        field_builder = schema_builder.AddSimpleField(field_name, field_type)




    # Register the schema
    schema = schema_builder.Finish()

    return schema

def update_schema_entity(schema, element, field_name, value):
    entity = DB.ExtensibleStorage.Entity(schema)

    field = schema.GetField(field_name)
    if not field:
        raise ValueError("No field found with the name: <{}> in schema: <{}>".format(field_name, schema.SchemaName))

    # entity.Set(field, value)
    if type(value) == int:
        entity.Set[int](field, value)
    elif type(value) == float:
        entity.Set[float](field, value)
    elif type(value) == bool:
        entity.Set[bool](field, value)
    elif type(value) == str:
        entity.Set[str](field, value)
        
    element.SetEntity(entity)


def get_schema_entity(schema, element, field_name, value_type):
    entity = element.GetEntity(schema)
    field = schema.GetField(field_name)
    return entity.Get<value_type>(field)