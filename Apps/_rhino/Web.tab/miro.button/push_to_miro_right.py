
__title__ = "PushToMiro"
__doc__ = "Push selected elements in Rhino to Miro. Only support text and rect and circle."

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def push_to_miro():
    print ("Sample func <{}> that does this:{}".format(__title__, __doc__))

#################
if __name__ == "__main__":
    push_to_miro()

