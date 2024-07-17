
__title__ = "Reload Python"
__doc__ = "Checkout pre-recorded turtorials and demos about EnneadTab."



def reload_python():
    import EnneadTab
    import imp
    imp.reload(EnneadTab)
    # reload(EnneadTab)
    print ("Python reloaded???")

if __name__ == "__main__":
    reload_python()