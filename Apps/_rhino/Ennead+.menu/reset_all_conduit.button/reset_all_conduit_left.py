
__title__ = "ResetAllConduit"
__doc__ = "Reset all conduits"

import scriptcontext as sc


def reset_all_conduit():
    print ("current stickys")
    print (sc.sticky.items())

    for key in sc.sticky.keys():
        if "conduit" in key.lower():
            conduit = sc.sticky[key]
            print ("removing sticky:" + key)

            # some old key also has conduit in name, but not as actal conduit obj
            if hasattr(conduit, "Enabled"):
                conduit.Enabled = False
            sc.sticky.pop(key)
