

from BaseHandler import BaseHandler
from GuidHandler import GuidHandler

class TabGroupHandler(BaseHandler):
    def __init__(self, tab):
        self.guid = GuidHandler(tab.tab_folder).guid
        self.major_version = 1
        self.minor_version = 1
        self.tab = tab
      

    def __repr__(self) -> str:
        return f"TabGroupHandler({self.tab_name})"


    def as_json(self):
        data = {
            "@guid": self.guid,
            "major_version": str(self.major_version),
            "minor_version": str(self.minor_version),
            "text": {"locale_1033": self.tab.tab_name},
            "tool_bar_id": self.tab.guid
            
        }
        data = {"tool_bar_group_item":data}
        return data

def get_tabgroups(tabs):
    return [TabGroupHandler(tab) for tab in tabs]



if __name__ == "__main__":
    pass