# EnneadTab-OS

![alt text](Apps\\lib\\EnneadTab\\images\\logo_ennead-e_200x200.png)

## This is the new, unified repository for the entire EnneadTab ecosystem.
- All assets and executables can be found here.
- This is a fresh start and a new deployment framework for EnneadTab; there are no external references.
- This repository is the development environment for EnneadTab; EnneadTab developers should clone to _Test/Dev AVD_ and work from there.
- End-user content is pushed to a separate, public repo [__EA_Dist__](https://github.com/zsenarchitect/EA_Dist).
- Over time, new apps will be integrated/consolidated here from separate repos.
- The current priority for EnneadTab-OS is to get the lib system working in Revit from outside the typical pyRevit libray location.
---
<br> 
<br>

> [!IMPORTANT]
> # How to contribute: 
> 1. Clone [__EnneadTab-OS__](https://github.com/zsenarchitect/EnneadTab-OS) and [__EA_Dist__](https://github.com/zsenarchitect/EA_Dist) repositories to _Test/Dev AVD_. 
> 2. From that point you can just leave __EA_Dist__ alone; no need to manually change anything.
> 3. Create and activate a virtual environment using python 3.8 or 3.10 in the root directory and install required modules (_see appendix A for instructions_). 
> 4. To make a new ___Rhino button___, run `.\Apps\_rhino\Ennead+.menu\create_new_button.button\new_button_left.py` in your IDE, or run "MakeANewButton" in Rhino. This will prepare your new folder and template script, but does not make new RUI file. 
> 5. To update the RUI file for Rhino, run `.\DarkSide\RuiWriter\__init__.py` in your IDE. After that, click __GetLatest__ in Rhino to see your new button in the UI.
> 4. To make a new ___Revit button___, click "Duck Maker" in Revit. This will prepare your new folder and template script and load to Revit UI.
> 5. To distribute the current stage of EnneadTab-OS, run `.\DarkSide\________publish.py` in the DarkSide. This will: 
>       - Recompile a new RUI
>       - Optionally recompile all executables.
>       - Update __Apps__ and __Installation__ folder in __EA_Dist__.
>       - Push to remote. You are done.
---
<br> 
<br>

> [!IMPORTANT]
> # How to help with testing:
> There are many ongoing rewrites and updates in the core modules, so the new system is not stable...yet.
> <br>In the order of priority, please help test these functions periodically:
> 1. Installation/Update
> 2. Notifications/Reports
> 3. Hooks 
> 4. Popular Tools 
> 5. Tailor Tools 
> 6. Less Popular Tools 
> 7. Fun Tools
---
<br> 

### __Appendix A:__ _creating and setting up a virtual environment for development_
#### Execute the following steps in your IDE terminal.
- `cd` to the root directory of this repository on your local machine.
- _Note: If you have `pyenv` installed on your machine, it will attempt to use Python 3.10.6, if available._
- `python -m venv .venv`
- `.venv\Scripts\activate`
- `python -m pip install --upgrade-pip`
- `pip install --upgrade wheel`
- `pip install -r requirements.txt`

### _Enjoy!_

