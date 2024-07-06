
__alias__ = "UpdateFromRepo"
__doc__ = "This button does UpdateFromRepo when left click"


import traceback
import clr # pyright: ignore


from Duckitect import ENVIRONMENT_CONSTANTS
LIBGIT_DLL = "{}\LibGit2Sharp.dll".format(ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_LEGACY)
clr.AddReferenceToFileAndPath(LIBGIT_DLL)

import LibGit2Sharp as libgit

def update_from_repo():
    repo_url = "https://github.com/zsenarchitect/EA_Dist.git"
    clone_dir = "C:\\Users\\szhang\\Documents\\Duckitect Ecosystem"
    clone_ops = libgit.CloneOptions()

    try:
        libgit.Repository.Clone(repo_url,
                                clone_dir,
                                clone_ops)
    except:
        print (traceback.format_exc())
