
from datetime import date
import pickle
import os

import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import DATA_FILE
import time
import FOLDER
try:
    
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass


def name_fix(name):
    new_name = ""
    for x in name:
        new_name += x
    if new_name != str(name):
        print ("File name renamed!")
    return new_name

def append_data(file,data_entry):
    if not os.path.exists(file):
        f = open(file, 'w')
        pickle.dump([data_entry], f)
        f.close()
        return

    f = open(file, 'r')
    current_data  = pickle.load(f)
    f.close()

    for item in current_data:
        if str(date.today()) in item:
            print ("warning data with this date {} exist already".format(date.today()))
            return


    f = open(file, 'w')
    current_data.append(data_entry)
    pickle.dump(current_data, f)
    f.close()


def read_data(file, doc):
    if not os.path.exists(file):
        print ("data with this file title {} do not exist".format(doc.Title))
        return None
    
    f = open(file, 'r')
    current_data  = pickle.load(f)
    f.close()
    return current_data

        




def compare_data(previous_data,current_warning_count, doc):



    old_date = previous_data.split(":")[0]
    old_warnings = int(previous_data.split(":")[1])

    #warning_count = len(revit.doc.GetWarnings())

    warning_increase = current_warning_count - old_warnings
    percentage = "{:.1%}".format(abs(warning_increase/float(old_warnings)))



    main_text = "{} warnings found.".format(current_warning_count)



    if warning_increase > 0:
        tmp_text = "increased"
        price = 1
        price_note = "Shared Cost:Deduct ${} per warning gained.".format(price)
    elif warning_increase < 0:
        tmp_text = "decreased"
        price = 2
        price_note = "Shared Benifit:Reward ${} per warning removed.".format(price)
    else:
        main_text += "\nThe same number as the count on {}.".format(old_date)
        return main_text




    main_text += "\nSince {}, the warning has {} by {}. A change of {}.".format(old_date, tmp_text, abs(warning_increase), percentage )
    # too big of a change might means new doc, then donot record money
    if abs(warning_increase/float(old_warnings)) > 0.9:
        return main_text

    main_text += "\n{}".format(price_note )
    if old_warnings != 0:
        ENNEAD_LOG.open_doc_with_warning_count(warning_count = warning_increase, doc = doc)

    return main_text


######################################################################################################################################


    
class WarningHistory:
    
    def __init__(self, doc):
        if isinstance(doc, str):
            self.doc_name = doc
            self.doc = None
        else:
            self.doc = doc
            self.doc_name = doc.Title
        self.file = "REVIT_WARNING_HISTORY_{}.json".format(self.doc_name)

        
        if os.path.exists(FOLDER.get_shared_dump_folder_file(self.file)):
            
            self.data = DATA_FILE.read_json_as_dict_in_shared_dump_folder(self.file, create_if_not_exist=True)
        else:
            print("data find not found")
            self.data = {}
    
    def record_warning(self):
        # in event where doc is not valid, there is no data to record to
        if not self.doc:
            print("doc obj not valid")
            return
        
        today = time.strftime("%Y-%m-%d")
        today_data = self.data.get(today, {})


        for warning in self.doc.GetWarnings():
            description = warning.GetDescriptionText()
            
            if self.doc.IsWorkshared:
                creators = list(set([DB.WorksharingUtils.GetWorksharingTooltipInfo (self.doc, x).Creator for x in warning.GetFailingElements()]))
            else:
                creators = []
            
            warning_cate_data = today_data.get(description, {})
            warning_cate_data["count"] = warning_cate_data.get("count", 0) + 1
            warning_cate_data["creators"] = list(set(warning_cate_data.get("creators", [])  + creators))
            
            today_data.update({description: warning_cate_data})
            
        self.data.update({today: today_data})
        DATA_FILE.save_dict_to_json_in_shared_dump_folder(self.data, self.file)
    
  
    def display_warning(self, show_detail=True):
        
        
        from pyrevit import script

        self.output = script.get_output()
        all_mentioned_warning_cates = []
        all_mentioned_users = []
        
        if not self.data:
            print("empty data")
            return

        
        print ("\n\n\n\n")
        self.output.insert_divider(level='')
        self.output.print_md ("# Document: {}".format(self.doc_name))
        if len(self.data.keys()) == 1:
            self.output.print_md ("### This document warning history has only been recorded once.")
        for date in sorted(self.data.keys()):
            date_data = self.data[date]
            
            self.output.insert_divider(level='') if show_detail else None
            self.output.print_md ("## Date: {}".format(date)) if show_detail else None
            all_mentioned_warning_cates += date_data.keys()
            for i, description  in enumerate( sorted(date_data.keys())):
                self.output.print_md ("\n\n{}".format(i+1)) if show_detail else None
                self.output.print_md ("Description: {}".format(description)) if show_detail else None
                warning_data = date_data[description]
                self.output.print_md ("Count: **{}**".format(warning_data["count"])) if show_detail else None
                self.output.print_md ("Creators: **{}**".format(warning_data["creators"])) if show_detail else None
                all_mentioned_users += warning_data["creators"]
                
        all_mentioned_warning_cates = sorted(set(all_mentioned_warning_cates))
        self.display_overall_status(all_mentioned_warning_cates)
        
        return

        # below is no longer processed becasue it is misleading
        all_mentioned_users = sorted(set(all_mentioned_users))
        map(lambda user: self.display_user_status(user, all_mentioned_warning_cates), all_mentioned_users)
                
                
    def display_overall_status(self, all_mentioned_warning_cates):
        # Line chart
        chart = self.output.make_stacked_chart()
        chart.set_style('height:150px')

        chart.options.title = {'display': True,
                            'text':'Revit File Warning History for [{}]'.format(self.doc_name),
                            'fontSize': 18,
                            'fontColor': '#000',
                            'fontStyle': 'bold'}
        
        # Set the legend configuration
        chart.options.legend = {
            'display': True,
            'position': 'bottom',  # Place the legend below the chart
            'labels': {
                'fontSize': 8,  # Customize the legend label font size
            }
        }
        
        # setting the charts x line data labels
        chart.data.labels = sorted(self.data.keys())
        

        # add data sets:
        for cate in all_mentioned_warning_cates:
            set_local = chart.data.new_dataset(cate)

            set_local.data = []

            # use exact same order as the X asix label
            for date in chart.data.labels:
                date_data = self.data[date]
                
                if cate in date_data:
                    set_local.data.append(date_data[cate]["count"])
                else:
                    set_local.data.append(0)

            # this make straight line.
            set_local.tension = 0

            

        chart.randomize_colors()

        chart.draw()



    def display_user_status(self, user, all_mentioned_warning_cates):
        # Line chart
        chart = self.output.make_stacked_chart()
        chart.set_style('height:350px')

        chart.options.title = {'display': True,
                            'text':'Revit File Warning History for [{}]-[{}]'.format(self.doc_name, user),
                            'fontSize': 18,
                            'fontColor': '#000',
                            'fontStyle': 'bold'}
        
        
        
        # setting the charts x line data labels
        chart.data.labels = self.data.keys()
        

        # add data sets:
        for cate in all_mentioned_warning_cates:
            set_local = chart.data.new_dataset(cate)

            set_local.data = []
            for date_data in self.data.values():
                if user not in date_data[cate]["creators"]:
                    set_local.data.append(0)
                else:
                    set_local.data.append(date_data[cate]["count"])
     
            
            set_local.tension = 0

            

        chart.randomize_colors()

        chart.draw()

        
def record_warning(doc):
    WarningHistory(doc).record_warning()



def display_warning(doc_name, show_detail=True):
    WarningHistory(doc_name).display_warning(show_detail)



if __name__ == "__main__":
    record_warning("temp2")