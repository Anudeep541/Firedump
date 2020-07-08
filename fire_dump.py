'''
Author: Jane1729
Date: 06-07-2020
Description: Dumps Forensic Artificats of Firefox in Windows
'''
from pathlib import Path
import sqlite3

profile_dbs = {}
usr_content = {}

def fire():

    #### Getting the users and storing in a list ####
    users = [x.name for x in Path(r'C:\Users').glob('*') if x.name not in ['Public', 'All Users'] and x.name.find('Default') and x.name.find('default') and x.is_dir()]
    #print (users)

    for usrname in users:
        folder_path = 'C:/Users/'+usrname+'/AppData/Roaming/Mozilla/Firefox/Profiles'
        ##### Getting the profiles in Firefox for a particular user #####
        folder_names = [f.name for f in Path(folder_path).glob('*')]

        if len(folder_names) == 0:
            continue

        else:
            for var in folder_names:
                profile_dbs.update({var:folder_path+'/'+var+'/places.sqlite'})          # Putting profile name and respective database path in a dictionary 
        usr_content.update({usrname:profile_dbs})                                       # Putting profiles and database paths of particular user in another dictionary

def db_bookmarks(db_loc):
    conn = sqlite3.connect(db_loc)
    cur = conn.cursor()
    cur.execute("select title,datetime(dateAdded/1000000,'unixepoch',,'localtime'),datetime(lastModified/1000000,'unixepoch','localtime') from moz_bookmarks")
    rows = cur.fetchall()

    for value in rows:
        print (value)
    conn.close()

def db_history(db_loc):
    connection = sqlite3.connect(db_loc)
    ruc = connection.cursor()
    ruc.execute("select url,title,visit_count,datetime(last_visit_date/1000000,'unixepoch',,'localtime') from moz_places")
    data = ruc.fetchall()

    for content in data:
        print (content)
    connection.close()

def db_downloads(db_loc):
    attach = sqlite3.connect(db_loc)
    pointer = attach.cursor()
    pointer.execute("select content,datetime(dateAdded/1000000,'unixepoch','localtime'),datetime(lastModified/1000000,'unixepoch','localtime') from moz_annos")
    info = pointer.fetchall()

    for raw in info:
        print (raw)
    pointer.close()


fire()

for usr in usr_content:
    profile = usr_content[usr]                              # Putting profile name and respective databasepath in other dictionary
    for name in profile:
        db_path = profile[name]                             # Getting database path of respective profile
        db_downloads(db_path)
