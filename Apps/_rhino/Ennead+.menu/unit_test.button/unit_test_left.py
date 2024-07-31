
__title__ = "UnitTest"
__doc__ = "This button does UnitTest when left click"


from EnneadTab import ERROR_HANDLE, LOG, UNIT_TEST
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def unit_test():
    UNIT_TEST.test_core_module()
    

    
if __name__ == "__main__":
    unit_test()
