import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import rhinoscriptsyntax as rs


class OutputColorStyle:
    BlackWhite = "BlackWhite"
    Color = "Color"
    GrayScale = "GrayScale"
    PrintColor = "PrintColor" # if print layout


class PaperSize:
    # @staticmethod
    def inch2mm(w, h):
        # return resut in round of 2 decimal
        return round(w * 25.4, 2), round(h * 25.4, 2)

    @staticmethod
    def mm2inch(w, h):
        return int(w / 25.4), int(h / 25.4)


    # this is needed for compability < py3.9, above decorator is abadoned
    # inch2mm = staticmethod(inch2mm)
    # mm2inch = staticmethod(mm2inch)

    
    """assuming all dimension in landscape for Arch drawings"""
    A0 = 1189,841
    A1 = 841,595
    A2 = 595,420
    A3 = 420,297
    A4 = 297,210
    A5 = 210,148


    Letter = inch2mm(11,8.5)
    Tabloid = inch2mm(17,11)
    Arch_A = A12x9 = inch2mm(12,9)
    Arch_B = A18x12 = inch2mm(18,12)
    Arch_C = A24x18 = inch2mm(24,18)
    Arch_D = A36x24 = inch2mm(36,24)
    Arch_E = A48x36 = inch2mm(48,36)

class ArchiScale:
    # @staticmethod
    def imperial2metric(imperial_scale):
        return imperial_scale * 12

    # this is needed for compability < py3.9, above decorator is abadoned
    # imperial2metric = staticmethod(imperial2metric)
 
    Metric_1000 = 1000
    Metric_500 = 500
    Metric_250 = 250
    Metric_200 = 200
    Metric_100 = 100
    Metric_50 = 50
    Metric_25 = 25
    Metric_20 = 20
    Metric_10 = 10
    Metric_5 = 5
    
    
    Imperial_128 = imperial2metric(128)
    Imperial_64 = imperial2metric(64)
    Imperial_32 = imperial2metric(32)
    Imperial_16 = imperial2metric(16)
    Imperial_8 = imperial2metric(8)
    Imperial_4 = Imperial_Quarter = imperial2metric(4)


    @staticmethod
    def get_source_key(scale):
        for key in ArchiScale.__dict__:
            if ArchiScale.__dict__[key] == scale:
                return key
        return None


    @staticmethod
    def print_scale(scale):
        is_metric = "metric" in ArchiScale.get_source_key(scale).lower()
        if is_metric:
            return "1:{}".format(scale)
        else:
            return "1/{}\" = 1\'0\"".format(int(scale/12))



#############################################################################
def print_pdf(filepath, 
              scale, 
              width, 
              height, 
              color_style = OutputColorStyle.Color):
    """scale need to be translated for true number sclae, there is no imoerial scale
    width and height always use mm regardless file unit,
    color style use the Enumrate Object
    """
    rs.Command("!_-Print Setup View Scale {} -Enter Destination Printer \"Microsoft Print to PDF\" PageSize {} {} OutputColor {} -Enter -Enter Go \"{}\" -Enter -Enter".format(scale,
                                                                                                                                                                                width,
                                                                                                                                                                                height,
                                                                                                                                                                                color_style,
                                                                                                                                                                                filepath))




def unit_test():
    # print all class variable of class PaperSize
    for size in PaperSize.__dict__:
        #  skip if this is a internal variable or a function
        if size.startswith("__") or callable(getattr(PaperSize,size)):
            continue


        mm_w, mm_h = PaperSize.__dict__[size]
        inch_w, inch_h = PaperSize.mm2inch(mm_w, mm_h)
        print ("\nStandard paper size [{}]\n{} x {} mm\n{} x {} in".format(size, 
                                                                            mm_w, mm_h,
                                                                            inch_w, inch_h))

    for scale in ArchiScale.__dict__:
        #  skip if this is a internal variable or a function
        if scale.startswith("__") or callable(getattr(ArchiScale,scale)):
            continue

        scale_num = ArchiScale.__dict__[scale]
        print ("\nArchiScale [{}]\n{} --> {} true value".format(scale, 
                                                     ArchiScale.print_scale(scale_num),
                                                     scale_num))
    
if __name__ == "__main__":
    unit_test()