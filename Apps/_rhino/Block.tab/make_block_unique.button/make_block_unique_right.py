__title__ = "MakeBlockUniqueToOne"
__doc__ = "Make a block unique on spot. All different types of block will merge to one new block"


from EnneadTab import LOG, ERROR_HANDLE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def make_block_unique():
    print ("this is inside right click of make block unique")


if __name__ == "__main__":
    make_block_unique()