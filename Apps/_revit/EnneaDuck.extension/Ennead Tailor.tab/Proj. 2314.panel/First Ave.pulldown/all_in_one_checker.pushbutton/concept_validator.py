CALCULATOR_FAMILY_NAME = "USF Calculator"
AREA_SCHEME_NAME = "Usable Area"
PARA_TRACKER_NAMES = ["(NON) USABLE",
                      "(NON) COMMON",
                      "(NON) COMMON-MECH",
                      "USABLE",
                      "USABLE MECH"]

class TestClass:
    def update(self, area_name, area):
        if not hasattr(self, area_name):
            setattr(self, area_name, area)
            return
        
        current_area = getattr(self, area_name)
        setattr(self, area_name, current_area + area)
        
data = TestClass()
for para_name in PARA_TRACKER_NAMES:
    data.update(para_name, len(para_name))
for x in dir(data):
    print(x)
    
for para_name in PARA_TRACKER_NAMES:
    print (getattr(data,para_name))