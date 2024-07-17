import time

from pyrevit import script




from EnneadTab import EXE, DATA_FILE, TIME, FOLDER

from Autodesk.Revit import DB # pyright: ignore  

# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


# citical warnings Guids
CRITICAL_WARNINGS = [
    "6e1efefe-c8e0-483d-8482-150b9f1da21a",
    # 'Elements have duplicate "Number" values.',
    "6e1efefe-c8e0-483d-8482-150b9f1da21a",
    # 'Elements have duplicate "Type Mark" values.',
    "6e1efefe-c8e0-483d-8482-150b9f1da21a",
    # 'Elements have duplicate "Mark" values.',
    "b4176cef-6086-45a8-a066-c3fd424c9412",
    # 'There are identical instances in the same place',
    "4f0bba25-e17f-480a-a763-d97d184be18a",
    # 'Room Tag is outside of its Room',
    "505d84a1-67e4-4987-8287-21ad1792ffe9",
    # 'One element is completely inside another.',
    "8695a52f-2a88-4ca2-bedc-3676d5857af6",
    # 'Highlighted floors overlap.',
    "ce3275c6-1c51-402e-8de3-df3a3d566f5c",
    # 'Room is not in a properly enclosed region',
    "83d4a67c-818c-4291-adaf-f2d33064fea8",
    # 'Multiple Rooms are in the same enclosed region',
    "ce3275c6-1c51-402e-8de3-df3a3d566f5c",
    # 'Area is not in a properly enclosed region',
    "e4d98f16-24ac-4cbe-9d83-80245cf41f0a",
    # 'Multiple Areas are in the same enclosed region',
    "f657364a-e0b7-46aa-8c17-edd8e59683b9",
    # 'Room separation line is slightly off axis and may cause inaccuracies.''
]


# use distinct color collection
COLORS = 10 * [
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#000000",
    "#fff0f2",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#e97800",
    "#a6c844",
    "#4d4d4d",
    "#fff0d9",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
    "#fff0e6",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#fff0e6",
    "#e97800",
    "#a6c844",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
    "#4d4d4d",
    "#fff0d9",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
    "#4d4d4d",
    "#fff0d9",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
    "#4d4d4d",
    "#fff0d9",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
    "#4d4d4d",
    "#fff0d9",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
    "#4d4d4d",
    "#fff0d9",
    "#ffc299",
    "#ff751a",
    "#cc5200",
    "#ff6666",
    "#ffd480",
    "#b33c00",
    "#ff884d",
    "#d9d9d9",
    "#9988bb",
    "#4d4d4d",
    "#e97800",
    "#a6c844",
]


class QAQC:
    def __init__(self, output):
        self.OUT = ""
        self.output = output

    def LOG(self, text, is_title = False):
        if is_title:
            line = "\n\n---\n# " + text
        else:
            line = "\n" + text
        self.output.print_md(line)
        self.OUT += line

    def proj_info_report(self):
        project_info_collector = doc.ProjectInformation
        self.LOG("Basic Info:", is_title =True)
        self.LOG("Proj. Number: {}".format(project_info_collector.Number))
        self.LOG("Project Name: {}".format(project_info_collector.Name))
        self.LOG("Client: {}".format(project_info_collector.ClientName))
        self.LOG("Document: {}".format(doc.Title))

    def warning_report(self):
        # get the total number of warnings in file.
        all_warnings = doc.GetWarnings()
        critical_warnings = filter(
            lambda x: x.GetFailureDefinitionId().Guid in CRITICAL_WARNINGS, all_warnings)
        self.LOG("Warnings Report: {} total warnings.".format(len(all_warnings)), is_title =True)
        if len(critical_warnings) > 0:
            self.LOG("In there, {} are critical.".format(len(critical_warnings)))

        usage = dict()
        for warning in critical_warnings:

            key = warning.GetDescriptionText()
            count = usage.get(key, 0)
            usage[key] = count + 1

        if len(critical_warnings) > 0:
            self.LOG("\nCritical Warnings")
            sorted_keys = sorted(usage.keys(), key=lambda x: usage[x])
            for key in sorted_keys:
                self.LOG("{} -- {}".format(usage[key], key))

        failed_elements = []
        user_personal_log = dict()
        warning_category = dict()
        for warning in all_warnings:
            current_count = warning_category.get(warning.GetDescriptionText (), 0)
            warning_category[warning.GetDescriptionText ()] = current_count + 1

            failed_elements.extend(list(warning.GetFailingElements()))

            creators = [DB.WorksharingUtils.GetWorksharingTooltipInfo(
                doc, x).Creator for x in warning.GetFailingElements()]
            for creator in creators:
                if not user_personal_log.has_key(creator):
                    user_personal_log[creator] = dict()
                current_log = user_personal_log[creator]

                current_log_data = current_log.get(warning.GetDescriptionText (), 0)

      
                current_log[warning.GetDescriptionText ()] = current_log_data + 1

        user_data = self.log_list_by_creator(failed_elements, "elements with warnings.", is_id_list = True)

        


        # warnings count overall category
        warning_count_per_category = self.output.make_doughnut_chart()
        warning_count_per_category.options.title = {
            "display": True,
            "text": "Warning Count by Category",
            "fontSize": 25,
            "fontColor": "#000",
            "fontStyle": "bold",
            "position": "bottom"
        }
        warning_count_per_category.options.legend = {
            "position": "top", "fullWidth": False}
        warning_count_per_category.data.labels = [user.encode('UTF-8') for user in warning_category.keys()]
        set_w = warning_count_per_category.data.new_dataset("Not Standard")
        set_w.data = [x for x in warning_category.values()]
        set_w.backgroundColor = COLORS
        warning_count_per_category.set_width(10)
        try:
            warning_count_per_category.draw()
        except:
            pass
        self.LOG("---")




        # warnings count per user doughnut
        warning_count_per_user_chart = self.output.make_doughnut_chart()
        warning_count_per_user_chart.options.title = {
            "display": True,
            "text": "Warning Element Count by User",
            "fontSize": 25,
            "fontColor": "#000",
            "fontStyle": "bold",
            "position": "bottom"
        }
        warning_count_per_user_chart.options.legend = {
            "position": "top", "fullWidth": False}
        warning_count_per_user_chart.data.labels = [user.encode('UTF-8') for user in user_data.keys()]
        set_w = warning_count_per_user_chart.data.new_dataset("Not Standard")
        set_w.data = [x for x in user_data.values()]
        set_w.backgroundColor = COLORS
        warning_count_per_user_chart.set_width(10)
        try:
            warning_count_per_user_chart.draw()
        except:
            pass


        #
        # warning counter per category per user
        for user, log_data in user_personal_log.items():
            self.LOG("---")
            #DATA_FILE.pretty_print_dict(log_data)

            warning_count_per_categoty_chart = self.output.make_pie_chart()
            warning_count_per_categoty_chart.options.title = {
                "display": True,
                "text": "Warning Element Count by Category for <{}>".format(user),
                "fontSize": 16,
                "fontColor": "#000",
                "fontStyle": "bold",
                "position": "bottom"
            }
            warning_count_per_categoty_chart.options.legend = {
                "position": "top", "fullWidth": True}
            warning_count_per_categoty_chart.data.labels = [
                description.encode('UTF-8') for description in log_data.keys()]
            set_w = warning_count_per_categoty_chart.data.new_dataset(
                "Not Standard")
            set_w.data = [x for x in log_data.values()]
            set_w.backgroundColor = COLORS
            warning_count_per_user_chart.set_width(10)
            try:
                warning_count_per_categoty_chart.draw()
            except:
                pass
            


    def get_chart_scale(self, legend):
        count = len(str(legend))
        #print count
        if count < 60:
            return 100
        elif count < 85:
            return 120
        elif count < 100:
            return 150
        else:
            return 180

    def group_report(self):
        # get the total number of groups.

        # if group used more than 10, should warn it
        def process_group(OST, note):
            all_groups = (DB.FilteredElementCollector(doc)
                          .OfCategory(OST)
                          .WhereElementIsNotElementType()
                          .ToElements())

            self.LOG("{} Report: {} total {}s.".format(note.capitalize(),
                                                       len(all_groups), note), is_title =True)
            self.log_list_by_creator(all_groups, note)
            type_data = dict()
            for group in all_groups:
                type_name = group.Name
                current_count = type_data.get(type_name, 0)
                type_data[type_name] = current_count + 1

            threshold = 10
            bad_types = [type_name for type_name, count in type_data.items() if count > threshold]
            if len(bad_types) > 0:
                self.LOG(
                    "Following {} have used too many times, please consider refactoring to detail item family.\nMax allowed count: {}".format(note, threshold))
                for type_name in bad_types:
                    self.LOG("Group Name = < {} >: {} counts".format(
                        type_name, type_data[type_name]))

        process_group(DB.BuiltInCategory.OST_IOSDetailGroups, "detail group")
        process_group(DB.BuiltInCategory.OST_IOSModelGroups, "model group")

    def dwg_report(self):
        # count import dwg
        all_dwgs = (
            DB.FilteredElementCollector(doc)
            .OfClass(DB.ImportInstance)
            .WhereElementIsNotElementType()
            .ToElements()
        )

        import_dwgs = [x for x in all_dwgs if not x.IsLinked]
        # linked_dwgs = all_dwgs - import_dwgs
        if len(import_dwgs) == 0:
            self.LOG("Import Dwg Report: There is no imported dwg, Nice!", is_title =True)
            return
        self.LOG("Import Dwg Report: {} total imported dwgs.".format(
            len(import_dwgs)), is_title =True)
        # self.LOG(log_list_by_creator(linked_dwgs), "linked dwg")
        self.log_list_by_creator(import_dwgs, "import dwg")
        self.LOG("Use dwg manager in EnneadTab to find and correct dwgs.")

    def in_place_family_report(self):
        # family.IsInPlace
        all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family)

        in_place_families = [x for x in all_families if x.IsInPlace]
        if len(in_place_families) == 0:
            self.LOG("In-Place Family Report: There is no in-place families, Nice!", is_title =True)
            return
        self.LOG("In-Place Family Report: {} total in-place families.".format(len(in_place_families)), is_title =True)
        self.log_list_by_creator(in_place_families, "in-place families")
        self.LOG("It is generally not a good solution to use in-place families, but there is always an exception. Talk with your ACE for alternative.")

    def view_template_report(self):
        self.LOG("View Template Usage Report:", is_title =True)
        all_views = DB.FilteredElementCollector(doc).OfClass(DB.View)
        # used_template_ids = [v.ViewTemplateId for v in all_views]
        all_true_views = [v for v in all_views if v.IsTemplate == False]
        all_templates = [v for v in all_views if v.IsTemplate == True]

        usage = dict()
        for view in all_true_views:
            template = doc.GetElement(view.ViewTemplateId)
            if not template:
                continue
            key = template.Name
            count = usage.get(key, 0)
            usage[key] = count + 1
        #print usage
        # sort usage dict by value, and retun as list`
        self.LOG("Count -- Template Name")
        usage_key_sorted = sorted(usage.keys(), key=lambda x: usage[x], reverse=True)
        for key in usage_key_sorted:
            self.LOG("{} -- {}".format(usage[key], key))

        unused_templates = [x for x in all_templates if x.Name not in usage_key_sorted]
        if len(unused_templates) > 0:
            for template in unused_templates:
                self.LOG("0 -- {}".format(template.Name))
            self.LOG("There are {} usused templates. Unused template can be purged. Considering removing template with Ideate Manager.".format(len(unused_templates)))

    def ref_plane_report(self):
        all_ref_planes = (
            DB.FilteredElementCollector(doc)
            .OfClass(DB.ReferencePlane)
            .ToElements()
        )
        # only get ref planes whoes workset is not read-only. Then we are geting the ref for project, not ref in the family.
        all_ref_planes = [x for x in all_ref_planes if not x.LookupParameter("Workset").IsReadOnly]
        
        
        self.LOG("Reference Plane Report: {} total reference planes.".format(
            len(all_ref_planes)), is_title =True)

        # for i,ref in enumerate( list(all_ref_planes)):
        #     print "{}:{}".format(i, ref.Name)
        


        unnamed_ref_planes = filter(
            lambda x: x.Name == "Reference Plane", all_ref_planes)
        if len(unnamed_ref_planes) == 0:
            self.LOG("\nThere are no unnamed reference planes. Nice!")
            return

        self.LOG("\nThere are {} unnamed reference planes.".format(len(unnamed_ref_planes)))
        if len(unnamed_ref_planes) > 20:
            self.LOG("\nThere are too many unnamed reference planes. Unnamed reference planes should be removed or named with intention.")

        self.log_list_by_creator(unnamed_ref_planes, "unnamed reference planes")

    def log_list_by_creator(self, list, note, is_id_list = False):

        user_data = dict()
        for x in list:
            if is_id_list:
                creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(
                    doc, x).Creator
            else:
                creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(
                    doc, x.Id).Creator
            count = user_data.get(creator, 0)
            user_data[creator] = count + 1

        for user, count in user_data.items():
            self.LOG("User < {} > has created {} {}.".format(user, count, note))

        return user_data

    def get_report(self, pdf_file=None, save_html = False):
        # first JS to avoid error in IE output window when at first run
        # this is most likely not proper way
        try:
            chartOuputError = self.output.make_doughnut_chart()
            chartOuputError.data.labels = []
            set_E = chartOuputError.data.new_dataset("Not Standard")
            set_E.data = []
            set_E.backgroundColor = ["#fff"]
            chartOuputError.set_height(1)
            try:
                chartOuputError.draw()
            except:
                pass
        except:
            pass

        #  try to open output window again if previously hidden
        try:
            self.output.show()
        except:
            return "PREVIOUSLY CLOSED"


        begin_time = time.time()
        self.proj_info_report()
        self.warning_report()
        self.ref_plane_report()
        self.group_report()
        self.dwg_report()
        self.in_place_family_report()
        self.view_template_report()

        used_time = time.time() - begin_time
        used_time = TIME.get_readable_time(used_time)
        self.LOG("\n\nTotal run time = {}".format(used_time))

        # for line in self.OUT.split("\n"):
        

        if save_html:
            file = FOLDER.get_EA_dump_folder_file("QAQC_REPORT_LOCAL.html")
            script.get_output().save_contents(file)
            EXE.open_file_in_default_application(file)



        if not pdf_file:
            return self.OUT

        # save text to pdf file


if __name__== "__main__":
    pass