# How to use AccFileOpenner


## why?
ACC Desktop Connector pioritise the sync of Autodesk product files. For other major softwares it can sync too, __but__ the connecter will not sync most of the lock file. So there are risk that multiple user will override file unitentitally.

## How to use?
![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_acc.png)
Keep the Openner.exe open. You can pick file/drop file to the window to make a local copy, create editing marker file on the acc folder so other users can see which file is occupied. If a second user want to open the same file, the tool will place a edit request file to queue the editing order.

When you close file, the editing marker file is removed from acc. When a second user want to open, their request marker file will be converted to a editing marker file.

Rhino, CAD, Indesign, Word and Excel have native lock file format that this tool can monitor. There is no action needed when exiting. Photoshop, Illustrator and PDF does not have lock file format, so you DO need to click "I am finished" to notify that you are no longer editing. The post process will handle the marker files cleanup.

The main display panel will lookup the current status of the ACC folders so you are aware where have the editing marker or request market file.

Word and Excel are prefered to edit in the cloud for its collbration ability, but if you do need to edit it locally, the tool also allow file lock for them.

## What file types are supported?
Files with default file lock system:
- Indesign
- Rhino
- Word
- Excel

Files without default file lock system:
- PDF
- Illustrator
- Photoshop
