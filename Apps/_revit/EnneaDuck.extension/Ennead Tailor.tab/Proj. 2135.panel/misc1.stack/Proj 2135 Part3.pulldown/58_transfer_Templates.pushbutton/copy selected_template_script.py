__doc__ = "Copy selected view templates to other open models."
__title__ = "58_Copy selected template to other open doc"
#pylint: disable=import-error,invalid-name
from pyrevit import revit
from pyrevit import forms
from Autodesk.Revit import DB # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

selected_viewtemplates = forms.select_viewtemplates(doc = doc)
t = DB.Transaction(doc, "temp")
t.Start()
for template in selected_viewtemplates:
    template.Name += "_Transfered from doc_{}".format(doc.Title)
if selected_viewtemplates:
    dest_docs = forms.select_open_docs(title = 'Select Destination Documents')
    if dest_docs:
        for ddoc in dest_docs:
            with revit.Transaction('Copy View Templates', doc = ddoc):
                revit.create.copy_viewtemplates(
                    selected_viewtemplates,
                    src_doc = doc,
                    dest_doc = ddoc
                    )
t.RollBack()
