# EnneadTab-OS

working plan:
1. start fresh, this is the new home of EVERYTHING, no external reference. All asset and exe access from within this folder
2. working env: the dev side only live in DEV AVD to ensure rule #1. The content is pushed to EA_Dist becasue that is a public repo and are ok to be wiped as needed....
3. each app is copied over from solo repo over time, the primary goal is to get the lib system to work for revit.It need to work ouside pyrevit typical lib location.



Desired structure for future planning....


<!-- important only -->
only keep one core module, and place it outside any app.
Figure out how to have pyRevit point to a lib path.