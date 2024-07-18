
__title__ = "TellMeVersion"
__doc__ = "This button does TellMeVersion when left click"


from EnneadTab import ERROR_HANDLE, LOG, VERSION_CONTROL

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def tell_me_version():
    VERSION_CONTROL.show_last_success_update_time()

    
if __name__ == "__main__":
    tell_me_version()
