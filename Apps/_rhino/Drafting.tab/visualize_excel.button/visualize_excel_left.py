
__alias__ = "VisualizeExcel"
__doc__ = "Convert excel data to shape diagrams."


import rhinoscriptsyntax as rs

import math

import textwrap


from Duckitect import NOTIFICATION
from Duckitect import DATA_FILE
from Duckitect import EXCEL

def visualize_excel():
    ShapeWriter().write_shape()

class ShapeWriter:

    @staticmethod
    def get_edge_L_from_area(area):
        return math.sqrt(area)
    
    @staticmethod
    def get_r_from_area(area):
        return math.sqrt(area/math.pi)

    @staticmethod
    def secure_text(input_text):
        return input_text
        """convert the unicode object to pythong string that can be displayed properly

        Args:
            input_text (str): _description_

        Returns:
            str: secured text
        """
        # print input_text
        # print type(input_text)
        
        if Duckitect.USER.is_SZ():
            filepath = Duckitect.FOLDER.get_EA_dump_folder_file("excel_area_data.txt")
            
       
            Duckitect.DATA_FILE.save_list_to_txt([input_text], filepath, end_with_new_line = False, use_encode = True)
            text = Duckitect.DATA_FILE.read_txt_as_list(filepath, use_encode = True)
            return text[0]
            return Duckitect.UNICODE.convert_unicode_to_string(input_text)
        else:
            return input_text
        # wrapper = textwrap.TextWrapper(width = 100)

        # return wrapper.fill(text = "".format(input_text))


    @staticmethod
    def extra_info( data):
        print ('############')

        # print (type(data[0]))
        cate = ShapeWriter.secure_text(data[0])
        room = ShapeWriter.secure_text(data[1])
        try:
            area = float(data[2])
        except:
            return cate, None, None, None, 1
        color = [data[3], data[4],data[5]]
        try:
            color = map(lambda x: int(x), color)
        except:
            print([data[3], data[4],data[5]])
            rs.MessageBox("This color data cannot read. [{}]".format(cate))
        
        try:
            if data[8] == "":
                count = 1
            else:
                count = int(data[8])
   
        except:
            count = 1
        return cate, room, area, color, count



    def __init__(self):
        path = rs.OpenFileName("Pick the source file for excel area data", filter= "Excel files (*.xlsx)|*.xlsx")
        
        if not path:
            return
        all_sheets = EXCEL.get_all_worksheets(path)
        sheet = rs.ListBox(all_sheets, "Pick the sheet for excel area data", title="Duckitect Visualize Excel")
        if not sheet:
            return
        self.datas = EXCEL.read_data_from_excel(path, worksheet = sheet)
        # print self.datas
        
        # filepath = Duckitect.FOLDER.get_EA_dump_folder_file("excel_area_data.txt")
        # for i, entry in enumerate(self.datas):
        #     text, num = entry[:2], entry[2:]
        #     Duckitect.DATA_FILE.save_list_to_txt(text, filepath, end_with_new_line = False, use_encode = True)
        #     text = Duckitect.DATA_FILE.read_txt_as_list(filepath, use_encode = True)
        #     self.datas[i] = text + num
        
        opt = rs.ListBox(["Circle", "Square", "Bar"], "What shape to use?",  title="Duckitect Visualize Excel")
        self.basic_shape = opt
        if opt == "Bar":
            self.fix_bar_width = rs.RealBox("What is the width of the bar?")



    
        self.pointer = [0,0,0]
        self.big_title_offset = DATA_FILE.get_sticky_longterm("viz_excel_big_title_offset", 100)
        self.small_title_offset = DATA_FILE.get_sticky_longterm("viz_excel_small_title_offset", 50)
        self.caption_text_drop = DATA_FILE.get_sticky_longterm("viz_excel_caption_text_drop", 10)
        self.row_gap = DATA_FILE.get_sticky_longterm("viz_excel_row_gap", 60)
        self.column_gap = DATA_FILE.get_sticky_longterm("viz_excel_column_gap", 40)
        self.use_hori = DATA_FILE.get_sticky_longterm("viz_excel_use_hori", 1)
        
        para_list = ["big_title_offset", "small_title_offset", "caption_text_drop", "row_gap", "column_gap", "use_hori"]
        
        res = rs.PropertyListBox(items = ["Big Title Offset", "Small Title Offset", "Caption Offset", "Row Gap", "Column Gap", "Use Horitional(1 = Yes, 0 = No)"],
                            values = [getattr(self, x) for x in para_list],
                            message = "Enter Data for Visualization Shape Control",
                            title = "Visualize Excel Area")
        for i, x in enumerate(para_list):
            setattr(self, x, float(res[i]))
            
            DATA_FILE.set_sticky_longterm("viz_excel_" + x , float(res[i]))
        
        
        self.current_small_category = None
  
        self.is_first_row = True
        self.is_first_column = True
        rs.EnableRedraw(False)
        
    def write_shape(self):
        if not hasattr(self, "datas"):
            NOTIFICATION.messenger(main_text="Excel data not read.")
            return
        map(self.process_data, self.datas)
        


    def process_data(self, data):
        
        print ("\n\nnew data = " + str(data))

        if data == ["","","","","","","", "", ""] or data == ["","","","","","",""]:
            return
        if (data[2] == "" or data[2] == "Area") and data[0] != "":
            self.make_big_title_text(data)
            return
        print(data)
        print (type(data))
        cate, room, area, color, count = ShapeWriter.extra_info(data)
        if room == "":
            room = cate
        center = [0,0,0]
        
        # print cate, room, area, color, count
        srfs = []
        for i in range(count):
          
            
            x = i % 5
            y = int(i / 5)
            if self.use_hori and count > 25:
                x, y = y, x
            
            if self.basic_shape == "Square":
                L = ShapeWriter.get_edge_L_from_area(area)
                pts = [[L/2, L/2, 0],
                        [-L/2, L/2, 0],
                        [-L/2, -L/2, 0],
                        [L/2, -L/2, 0]]
                pts = [rs.PointAdd(pt, [x * L, y * L, 0]) for pt in pts]
                srfs.append(rs.AddSrfPt(pts))
                abstract_gap = L/2 
                
                
            elif self.basic_shape == "Circle":
                r = ShapeWriter.get_r_from_area(area)
                center = rs.PointAdd([0,0,0], [x * r * 2 , y * r * 2, 0])
                circle = rs.AddCircle(center, r)
                srfs.append( rs.AddPlanarSrf(circle))
                rs.DeleteObject(circle)
                abstract_gap = r 

            elif self.basic_shape == "Bar":
                W = self.fix_bar_width
                L = area/W
                pts = [[W/2, L/2, 0],
                        [-W/2, L/2, 0],
                        [-W/2, -L/2, 0],
                        [W/2, -L/2, 0]]
                pts = [rs.PointAdd(pt, [x * W, y * L, 0]) for pt in pts]
                srfs.append(rs.AddSrfPt(pts))
                abstract_gap = W/2
        
        
        caption_text_drop = max(self.caption_text_drop, abstract_gap + 5)
            
            
        [rs.ObjectColorSource(srf, 1) for srf in srfs]
        [rs.ObjectColor(srf, color) for srf in srfs]




        

        text_center = [0, -caption_text_drop, 0]
        note = int(area) if count == 1 else "{} x {}".format(int(area), count)
        text = rs.AddText("{}\n{}".format(room, note), text_center, justification = 2)


        collection = [text]
        collection.extend(srfs)


        group = rs.AddGroup()
        rs.AddObjectsToGroup(collection,group)

        if cate != self.current_small_category:   
            self.make_small_title_text(cate)
    
        if self.is_first_column:
            self.is_first_column = False
        else:
            self.pointer = rs.PointAdd(self.pointer, [self.column_gap, 0, 0])
            
        self.pointer = rs.PointAdd(self.pointer, [abstract_gap, 0, 0])
        rs.MoveObjects(collection, self.pointer)

       



    def make_small_title_text(self, cate):

 
        # Wrap this text.

        wrapper = textwrap.TextWrapper(width = 12)

        cate_new = wrapper.fill(text = cate)

        self.current_small_category = cate_new
        """
        if len(cate) > 12:
            cate = cate.replace(" ", "\n")
        """

    
        if self.is_first_row:
            self.pointer =[0,self.pointer[1],0]
            self.is_first_row = False
        else:
            self.pointer = rs.PointAdd([0,self.pointer[1],0], [0, -self.row_gap, 0])   
            
        small_title_location = rs.PointAdd([0,self.pointer[1], 0], [-self.small_title_offset, 0, 0])
        try:
            rs.AddText(cate_new, small_title_location, height = 2)
        except:
            rs.AddText(cate, small_title_location, height = 2)
        self.is_first_column = True

    def make_big_title_text(self, data):
        title = ShapeWriter.secure_text(data[0])
        area = data[6]
        

        
        # Wrap this text.
        wrapper = textwrap.TextWrapper(width = 12)

        title_new = wrapper.fill(text = title)
        self.current_big_category = title_new
        """
        if len(cate) > 12:
            cate = cate.replace(" ", "\n")
        """
        print ("#######")
        print (title_new)
        big_title_location = rs.PointAdd([0,self.pointer[1], 0], [-self.big_title_offset, 0, 0])
        if self.is_first_row:
            pass
        else:
            big_title_location = rs.PointAdd(big_title_location, [0, -self.row_gap, 0])   
            

        try:
            rs.AddText(title_new, big_title_location, height = 3)
        except:
            rs.AddText(title, big_title_location, height = 3)
        rs.AddText(str(int(area)), rs.PointAdd(big_title_location, [0, -self.row_gap*0.5, 0]), height = 3)

