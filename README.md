# quick-portal-publisher
A script to quickly publish local feature classes to a portal without the use of desktop software. This is meant for quickly setting up a testing environment for support cases. 

### How to run 
1) Jupyter Notebook 

Download the .ipynb file and save to a location on your machine where Jupyter Notebooks has access to. 
Start up the Jupyter Notebook instance (it will show up as a program in the start menu). A browser window will appear with the root directory displayed. Open the downloaded notebook and make custom changes (username, password, file paths) before running the notebook. 

2) Python Script

Download the .py file. To edit the file in IDLE, ensure you edit using the Pro instance (Python 3.x). Make custom changes (username, password, file paths) before running the script. Then, run the script (F5 in IDLE).

### Variables to modify in the script
`paths` - dictionary containing keys (feature class types) and values (their corresponding local file paths). <br>
`username` - your portal username.<br>
`password` - (optional) your portal password.<br>
`portalURL` - your portal URL. <br>
`clearTempWorkspace` - set this to True to delete the temporary folder that is created in your arcpy scratch workspace after the script is done running. <br>
`removeGDB` - set this to True to remove the file geodatabase item that is uploaded to your portal after the feature service is published from it. Note that you cannot overwrite the data of the hosted feature service if this file geodatabase item is deleted.  <br>
`fsName` - provide a feature service name. The feature layers in the service will have a timestring appended to their name to ensure uniqueness. Note: if the name already exists in your portal, the script will get mad at you. <br>
`tags` - provide any tags you want to include, separated by commas. <br>
`folder` - provide folder that you want to use in your portal. The default is root ('/'). The folder should exist before publishing (i.e. 'DeveloperData').<br>
`fcList` - a list of feature class types to publish (i.e. the keys of the `paths` dictionary listed previously). <br>

### Notes

The script will get mad at you if: 
- Paths to feature classes on your machine are invalid
- Your portal credentials are invalid 
- You try to publish a service with a title that already exists in the portal 

Other functionality: 
- You can delete hosted feature services from the script by uncommenting the code at the bottom of the script. You will need to provide the title of the item and then manually copy and paste the item ID that appears in the search output into the delete function on the next line. These are two separate functions so that you don't accidentally delete a service all in one go. (AHHH!) 
