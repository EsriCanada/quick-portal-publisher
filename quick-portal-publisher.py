#!/usr/bin/env python
# coding: utf-8

# # Publish Sample Data to Portal
# 
# Note: This does not create sd (service definition) files. It only creates hosted feature services. 
# 
# ### List of VMs available for testing
# 
# __Enterprise 10.7__<br>
# IP: 172.31.9.151 <br>
# Portal URL: https://tsvmdev107w2k16.tssupport.int/portal/ 
# 
# ~~__Enterprise 10.6__~~  
# ~~IP: 172.31.9.131~~     
# ~~Portal URL: https://tsvmdev106.tssupport.int/portal/~~
# 
# __Enterprise 10.5__ (not turned on) <br>
# IP: -- <br>
# Portal URL: https://tsvmdev105.tssupport.int/portal/ 
# 
# ### Login formats for username and portal/organization
# 
# Note: If logging into ArcGIS Enterprise, it is assumed that you are using your own portal credentials (not admin accounts).
# 
# __AGOL Organizational Account__ <br>
# `gis = GIS("https://www.arcgis.com", "username", "password")`
# 
# __Enterprise built-in account__ <br>
# `gis = GIS("https://portalname.domain.com/webadapter_name", "sharinguser")`
# 
# __Enterprise web-tier authentication with LDAP__ <br>
# `gis = GIS("https://portalname.domain.com/webadapter_name", "amy", "password")`
# 
# __Enterprise portal-tier authentication with Active Directory__ <br>
# `gis = GIS("https://portalname.domain.com/webadapter_name", "AVWORLD\\Publisher", "password")`
# 
# __Enterprise portal-tier authentication with LDAP__ <br>
# `gis = GIS("https://portalname.domain.com/webadapter_name", "sharing1", "password")`
# <br>
# 
# <hr>
# 

# ### Sample server data (for reference)
# 
# Version 9.31: https://sampleserver2.arcgisonline.com/arcgis/rest/services/ <br>
# Version 10.01: https://sampleserver1.arcgisonline.com/arcgis/rest/services/ <br>
# Version 10.02: https://sampleserver4.arcgisonline.com/arcgis/rest/services/ <br>
# Version 10.05: https://sampleserver3.arcgisonline.com/arcgis/rest/services/ <br>
# Version 10.6: https://server.arcgisonline.com/arcgis/rest/services/ <br>
# Version 10.6: https://services.arcgisonline.com/ArcGIS/rest/services/ <br>
# Version 10.71: https://sampleserver5.arcgisonline.com/arcgis/rest/services/ <br>
# Version 10.71: https://sampleserver6.arcgisonline.com/arcgis/rest/services/
# 

# ## Data sources

# ### Local default data (modify if needed)

# In[ ]:


''' Dictionary of data paths (can change paths to other folders on your local machine)
'''

# Import arcpy
import arcpy

# Eventually make this not dependent on ArcTutor folder 
# Add custom paths if have additional data for publishing 
paths = {
    'temp': arcpy.env.scratchFolder,
    'points_small': r'C:\arcgis\ArcTutor\BuildingaGeodatabase\Montgomery.gdb\Water\Tanks',
    'lines_small': r'C:\arcgis\ArcTutor\BuildingaGeodatabase\Montgomery.gdb\Landbase\Roads_cl',
    'polygons_small': r'C:\arcgis\ArcTutor\BuildingaGeodatabase\Montgomery.gdb\Landbase\Blocks',
    'points_large': r'C:\arcgis\ArcTutor\Data Reviewer\California.gdb\Landmarks\Buildings',
    'lines_large': r'C:\arcgis\ArcTutor\Data Reviewer\California.gdb\Transportation\MajorRoads',
    'polygons_large': r'C:\arcgis\ArcTutor\Data Reviewer\California.gdb\Boundaries\UrbanAreas'
}


# ## Enter user variables:

# In[ ]:


# Login (AGOL or Enterprise) - follow the examples above to select proper format for portal URL and username 
username = '' # enter username here
password = ''  # Leave blank to be prompted later for password
portalURL = '' # i.e. "https://tsvmdev107w2k16.tssupport.int/portal/"


# Clear temporary workspace after fgdb is published? 
clearTempWorkspace = True 


# Remove gdb from portal once layers are published?
# NOTE: If you delete a shapefile, file geodatabase, or CSV file, the Overwrite option on the hosted feature layer's 
# item page is no longer available. (https://doc.arcgis.com/en/arcgis-online/reference/faq.htm#DELETE_SRC)
removeGDB = True


''' Portal settings 
''' 

# Specify a feature layer (or feature layer collection) name and tags for portal item 
fsName = '' # leave blank for randomly generated name, or enter the name of the Hosted Feature Service
tags = 'sampledata, test'
folder = '/'  # root is '/', folder should exist before publishing (i.e. 'DeveloperData')


# Specify which features to publish in same feature service 
fcList = ['points_large', 'points_small'] # i.e. ['points_small', 'points_large']


# ## In menu bar, click Cell > Run All Below to run rest of script 

# In[ ]:


''' Log into AGOL or Enterprise 
''' 

from arcgis.gis import GIS

# Enter password below
if password == '':
    gis = GIS(portalURL, username=username)
else:
    gis = GIS(portalURL, username=username, password=password)
print("Logged in as " + str(gis.properties.user.username))


# In[ ]:


''' Other Imports 
'''

import os, sys, time, shutil 
import zipfile


# ### Function list

# In[ ]:


''' FUNCTION --> createNewGDB
''' 

def createNewGDB(tempFolderPath, gdbName):
    
    out_gdb_path = os.path.join(tempFolderPath, gdbName)
    
    # Create new geodatabase 
    arcpy.CreateFileGDB_management(tempFolderPath, gdbName)
    
    return out_gdb_path


''' FUNCTION --> addFCtoGDB 
''' 
# Note: this assumes ArcTutor folder is current arcpy workspace  
    
def addFCtoGDB(gdbPath, fcID, timeString):
    
    # Set workspace and fc  
    arcpy.env.workspace = paths['temp']
    fc_path = paths[fcID] 
    
    # Name and path of new fc 
    fc_name = fcID + "_" + timeString
    out_fc_path = os.path.join(gdbPath, fc_name)
    print("Out FC: " + out_fc_path)

    # Copy feature class into gdb 
    arcpy.CopyFeatures_management(fc_path, out_fc_path)
    
    return out_fc_path


''' FUNCTION --> zipws 
    Source code: https://desktop.arcgis.com/en/arcmap/latest/analyze/sharing-workflows/h-zip-python-script.htm
'''
# Function for zipping files. If keep is true, the folder, along with all its contents, will be written to the zip file. 
# If false, only the contents of the input folder will be written to the zip file - the input folder name will not 
# appear in the zip file.

def zipws(path, zipfile, keep):
    path = os.path.normpath(path)
    # os.walk visits every subdirectory, returning a 3-tuple of directory name, subdirectories in it, and file names in it.
    #
    for (dirpath, dirnames, filenames) in os.walk(path):
        # Iterate over every file name
        #
        for file in filenames:
            # Ignore .lock files
            #
            if not file.endswith('.lock'):
                #print("Adding %s..." % os.path.join(path, dirpath, file))
                try:
                    if keep:
                        zipfile.write(os.path.join(dirpath, file),
                        os.path.join(os.path.basename(path), os.path.join(dirpath, file)[len(path)+len(os.sep):]))
                    else:
                        zipfile.write(os.path.join(dirpath, file),            
                        os.path.join(dirpath[len(path):], file)) 
                        
                except Exception as e:
                    print("Error adding %s: %s" % (file, e))

    return None


''' FUNCTION --> createZippedGDB 
'''
# Create the zip file for writing compressed data. In some rare
#  instances, the ZIP_DEFLATED constant may be unavailable and
#  the ZIP_STORED constant is used instead.  When ZIP_STORED is
#  used, the zip file does not contain compressed data, resulting
#  in large zip files. 

def createZippedGDB(gdbPath, outputPath):

    # Variables
    gdbName = os.path.basename(gdbPath).split(".")[0]
    zipName = gdbName + ".zip"
    zipPath = os.path.join(outputPath, zipName)

    try:
            zip_file = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
            zipws(gdbPath, zip_file, True)
            zip_file.close()
    except RuntimeError:
            # Delete zip file if it exists
            if os.path.exists(zipPath):
                    os.unlink(zipPath)
            zip_file = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_STORED)
            zipws(gdbPath, zip_file, True)
            zip_file.close()
            print("Unable to compress zip file contents.")
            sys.exit()

    print("Zip file created successfully: " + zipName)
    return zipPath


# In[ ]:


''' Setup and checks for script 
'''

# Create temp folder in scratch folder if not one already there 
outFolderPath = os.path.join(paths['temp'], 'temp')
if not os.path.exists(outFolderPath):
    os.makedirs(outFolderPath)
    
# Check to make sure local data paths are valid 
for fcID in fcList: 
    if not arcpy.Exists(paths[fcID]):
        raise RuntimeError("Error - the path " + paths[fcID] + " does not exist. Please enter a valid path in the data dictionary.")

    
''' Create new geodatabase and add feature classes
'''    

# Append current time to gdb name for unique name
timestr = time.strftime("%Y%m%d_%H%M%S")
    
# Name and path of new gdb
gdbName = ''
if fsName == '': 
    gdbName = "TestService_" + timestr
else: 
    gdbName = fsName 

# Check to make sure name doesn't already exist in portal
query = "title:" + gdbName 
searchResult = gis.content.search(query=query, item_type="Feature Service")
if searchResult:
    raise RuntimeError("Error: A feature service with this name already exists in the portal! Please specify a new name and try again.")

# Create gdb (if using custom FS name, append timestring to keep the gdb unique in local temp folder in case of duplicates)
if fsName == '': 
    tempGdbPath = createNewGDB(outFolderPath, (gdbName + ".gdb"))
else:
    tempGdbPath = createNewGDB(outFolderPath, (gdbName + "_" + timestr + ".gdb"))
    
# Add feature classes to new gdb 
for fcID in fcList: 
    print("Adding " + fcID + " to gdb")
    addFCtoGDB(tempGdbPath, fcID, timestr)

    
''' Zip geodatabase 
'''      
    
# Zip GDB
zippedGdbPath = createZippedGDB(tempGdbPath, outFolderPath)


# ### Import file geodatabase to portal and publish as hosted feature layer

# In[ ]:


''' Source code: https://developers.arcgis.com/labs/python/import-data/
'''

# Future portal item properties once published ************************* add more properties - also, want title to include date?
zippedGdbProperties = {
    'title': gdbName,
    'tags': tags,
    'type': 'File Geodatabase'
}

# Import file geodatabase to AGOL 
gdbImported = gis.content.add(zippedGdbProperties, data=zippedGdbPath, folder=folder)
print("Added fgdb item to AGOL")

# Now publish gdb item as hosted feature layer
hostedLayerItem = gdbImported.publish()
print("Published file geodatabase as hosted feature layer:")
print(hostedLayerItem.url)

# Remove gdb from portal after published  
if removeGDB: 
    # Remove from portal 
    print("Removing GDB from portal...")
    itemForDeletion = gis.content.get(gdbImported.id)
    itemForDeletion.delete()

# Remove temp folder from ArcTutor folder 
if clearTempWorkspace: 
    print("Removing temp folder: " + outFolderPath)
    shutil.rmtree(outFolderPath)


# ### Code to delete hosted feature service if necessary 

# In[ ]:


''' FUNCTION --> deletePortalFS 
    Delete feature service on portal 
'''

def findPortalFS(itemTitle): 
    # Search for existing feature service 
    query = "title:" + itemTitle 
    search_result = gis.content.search(query=query, item_type="Feature Service")
    if not search_result: 
        print("No items found!")
    else: 
        for res in search_result: 
            print(res.title + " --> ID: " + res.id)
            
def deletePortalFS(itemID):
    item_for_deletion = gis.content.get(itemID)
    print("Removing hosted FS " + item_for_deletion.title + " from portal...")
    item_for_deletion.delete()


# In[ ]:


''' Uncomment the code below (one line at a time) to run delete functions (if necessary)
'''

# Find and delete the feature service (FS) that was just created with this script
#findPortalFS('*') # enter name of FS title here (can use wildcard * in title if needed)


# In[ ]:


# copy and paste ID here of the item you want to delete (listed in output of findPortalFS method)
#deletePortalFS('') 

