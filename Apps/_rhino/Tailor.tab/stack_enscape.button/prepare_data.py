


import os

def get_collection_pairs(study):
    
    root_folder = r"J:\1643\1_Presentation\01_P-Base\01_Base Renderings\{}".format(study)
    glass_version_folder = r"{}\glass version".format(root_folder)
    chrome_version_folder = r"{}\chrome version".format(root_folder)

    collection_pairs = []
    glass_versions = sorted(os.listdir(glass_version_folder))
    glass_versions = [x for x in glass_versions if not x.endswith(".db")]

    # bundle_count = 8
    # #get the last n files from glass versions, that is the most recent n exports
    # glass_versions = glass_versions[-bundle_count:]
    # assert len(list(set([x.split("_")[-1] for x in glass_versions]))) == bundle_count, "there should be {} glass versions".format(bundle_count) 
    
    
    chrome_versions = sorted(os.listdir(chrome_version_folder))[::-1]
    for glass_version in glass_versions:
        view_name = glass_version.split("_")[-1]
        for chrome_version in chrome_versions:
            if view_name in chrome_version:
                

                # if this pair file is 10 mins older than glass version file then continue
                glass_version_file_path = os.path.join(glass_version_folder, glass_version)
                pair_file_path = os.path.join(chrome_version_folder, chrome_version)
                if (os.path.getmtime(glass_version_file_path) - os.path.getmtime(pair_file_path)) > 60*10:
                    continue
                break
        else:
            pair_file_path = "placeholder as long as it is not None"
        collection_pairs.append([os.path.join(glass_version_folder,glass_version),
                                pair_file_path])


    # print ("\n".join([str(pair) for pair in collection_pairs]))


    return collection_pairs
   



#####################
if __name__ == "__main__":
    print (get_collection_pairs("solar_panel"))