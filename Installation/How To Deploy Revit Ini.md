# Deploy Revit.ini file for all version of Revit
## this can work for either standalone computer or AVD image builder

example for what to do when Revit 2026 is released.

1. go to working folder __"L:\4b_Applied Computing\01_Revit\Initialization"__ prepare Revit.ini file for 2026 year version, make change if needed(set default family template path to L drive, etc). Changes are to be confirmed by Gayatri. We will keep one Revit.ini file per folder because Revit separate them by folder. __Add install markup for any changes you want to add.__
2. Download __https://github.com/zsenarchitect/EA_Dist/blob/main/Installation/RevitIniDeployer.exe__ and run. This will try to find all years versions and copy to ProgramData version ini for each year.
