# EnneadTab-OS

![alt text](Apps\\lib\\EnneadTab\\images\\logo_ennead-e.png)



working plan:
1. start fresh, this is the new home of EVERYTHING, no external reference. All asset and exe access from within this folder
2. working env: the dev side only live in DEV AVD to ensure rule #1. The content is pushed to EA_Dist becasue that is a public repo and are ok to be wiped as needed and limit the content for public....
3. each app is copied over from solo repo over time, the primary goal is to get the lib system to work for revit.It need to work ouside pyrevit typical lib location.

> [!IMPORTANT]
> # How to contribute: 
> 1. Clone __EnneadTab-OS__ and __EA_Dist__ repo to your computer. Don't need to ever touch EA_Dist, just let it be there.
> 2. Create venv. with python 3.8 or 3.10 in EnneadTab-OS. Install packages from "requirement.txt"
> 3. To make a new Rhino button, run "Apps\\_rhino\Ennead+.menu\create_new_button.button\new_button_left.py" in IDE. This will prepare your the new folder and template script, but does not make new .rui file. To make that into .rui, run RuiWriter's init.py. After that, click __GetLatest__ in rhino to see it shows up in UI.
> 4. To make a new Revit button, click "Duck Maker" in Revit. This will prepare your the new folder and template script and load to Revit UI.
> 5. To distribute the current stage of EnneadTab-OS, run ____publish.py in the DarkSide. This will recompile new .rui, recompile all exes(optional), and update __Apps__ and __Installation__ folder in EA_Dist, then push to remote. You are done.


> [!IMPORTANT]
> # How to help testing:
> There are many rewrite on the core moudle, so new system is not stable...yet.
> In the order of piority, please help test those functions periodically.
> Instalation/Update > Notification/Report > Hooks > Popular Tools > Tailor Tools > Less Popular Tools > Fun Tools


# What computer to use for Sen Zhang

### szhang2
- production working revit rhino
    - enneadtab for rhino(working)
    - enneadtab for revit(working)
- no OS
- no Dist


### szhang
- not in use.

### AVD GPU
- Amemeer says do not use

### AVD dev
- developemt for OS


### AVD image
- reserve for use when instructred by Amemeer

### dell laptop
- reserve for traveling days


### surface laptop
- reserve for traveling days


