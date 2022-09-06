from asyncio.windows_events import NULL
import json
from pickle import NONE, TRUE
import time
from datetime import datetime
from openpyxl import Workbook, load_workbook
from sqlConnection import _MYSQL, _MYSQL_INSERT
from jaarrekeningen import scrape_jaarrekeningen
from webScraper import scrape_website
from threading import Thread
# test
def test():
    return ["test1","test2","test3"]


# reading xcel data 
readingXcel = False
loginfo = "nothing"
def GetxcelData():
    global readingXcel
    global loginfo 
    df_durabilitycategories = _MYSQL('''SELECT dc.name as "Category",dt.name as "Term",dt.description as "Description",dk.ID as "KeyWordID",dk.name as "KeyWord" FROM scrape.durabilitycategories as dc INNER JOIN scrape.durabilityterms as dt ON dc.name = dt.durabilitycategoriesID INNER JOIN scrape.durabilitykeywords as dk ON dt.name = dk.durabilityterms;''')
    if(readingXcel is False):
        readingXcel = True
        #while True:
        try:
            #log that xcel is going to be red
            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':'Starting the process to read the xcel' })
            loginfo = f"data:{json_data}\n\n"
            #get xcel
            wb = load_workbook("C:/Users/kevin/Documents/prioritieitenlijst.xlsx") # "C:/Users/arvid/Documents/xcel/ondernemingsnummers.xlsx"
            ws = wb.get_sheet_by_name('Oost-Vl') # West-Vl Antwerpen Limburg Vl-Brabant
            firstrow = True

            for row in ws.rows:
                json_data = NULL
                # check if the first row has the column "Naam"
                if ((row[1].value != "Naam") and firstrow):
                    json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':  'sheet did not have the correct columns to be read' })
                    break
                # skip the first row
                if( firstrow ):
                    firstrow = False
                    json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':  'sheet has the correct columns to be read' })
                else:

                    # check if ID is already present in the DB
                    print("checking for "+row[9].value)
                    df_check = _MYSQL('''SELECT * FROM scrape.kmo where ID = '{}';'''.format(row[9].value))
                    if(df_check.empty):
                        print("no kmo with ID was found")
                        # check if municipality already excists
                        df_municipality_check = _MYSQL('''SELECT * FROM scrape.municipality where zipcode = '{}';'''.format(row[13].value))
                        if(df_municipality_check.empty):
                            print("New municipality found: ({})".format(row[13].value+","+row[2].value))
                            # add new municipality
                            _MYSQL_INSERT('''INSERT INTO scrape.municipality (zipcode, name) VALUES ({});'''.format(row[13].value+",'"+row[2].value+"'"))
                        # temp loging
                        print("executing:")
                        # fix website import
                        cleaned_website = NULL
                        if(row[14].value):
                            cleaned_website = "'"+ row[14].value+"'"
                            if(str.__contains__(cleaned_website, "HYPERLINK(")):
                                cleaned_website = "'"+ fix_hyperlink(row[14].value)+"'"
                        
                        # fix email import
                        cleaned_email = NULL
                        if(row[8].value):
                            cleaned_email =  "'"+ row[8].value+"'"
                            if(str.__contains__(cleaned_email, "HYPERLINK(")):
                                cleaned_email =  "'"+ fix_hyperlink(row[8].value)+"'"
                            if(str.__contains__(cleaned_email, "mailto://")):
                                cleaned_email =  cleaned_email.replace("mailto://","")

                                
                        print('''call insertAdress('{kmo_name}',{kmo_person},'{kmo_telephone}',{kmo_email},'{kmo_ID}',{kmo_website},{kmo_b2b},'{adres_street}',{adres_zipcode},{finance_omzet},{finance_total_value},{finance_netto_toe});'''.format(
                            kmo_name = row[1].value , kmo_person = row[3].value , kmo_telephone = row[7].value , kmo_email = cleaned_email , kmo_ID = row[9].value , kmo_website = cleaned_website , kmo_b2b = 0, 
                            adres_street = row[12].value , adres_zipcode = row[13].value , 
                            finance_omzet = row[4].value , finance_total_value = row[5].value, finance_netto_toe = row[10].value
                        ))
                        # add new kmo 
                        _MYSQL_INSERT('''call insertAdress('{kmo_name}',{kmo_person},'{kmo_telephone}',{kmo_email},'{kmo_ID}',{kmo_website},{kmo_b2b},'{adres_street}',{adres_zipcode},{finance_omzet},{finance_total_value},{finance_netto_toe});'''.format(
                            kmo_name = row[1].value , kmo_person = row[3].value , kmo_telephone = row[7].value , kmo_email = cleaned_email , kmo_ID = row[9].value , kmo_website = cleaned_website , kmo_b2b = 0, 
                            adres_street = row[12].value , adres_zipcode = row[13].value , 
                            finance_omzet = row[4].value , finance_total_value = row[5].value, finance_netto_toe = row[10].value
                        ))
                        # add sector tags 
                        sector_tags = split_into_sector_tags(row[15].value)
                        print(sector_tags)
                        for tag in sector_tags:
                            # check if tag already exists
                            print('''SELECT * FROM scrape.sector where name = '{}';'''.format(tag))
                            df_sectr_check = _MYSQL('''SELECT * FROM scrape.sector where name = '{}';'''.format(tag))
                            if(df_sectr_check.empty):
                                # add new ref and sector
                                _MYSQL_INSERT('''call insertSectorRef_and_sector('{}','{}');'''.format(row[9].value,tag))
                            else:
                                # add new ref
                                _MYSQL_INSERT('''INSERT INTO scrape.sectorlist (kmoID,sectorID) VALUES ('{}',{});'''.format(row[9].value,df_sectr_check.iloc[0].ID))

                        # scrape website the new kmo
                        print("going to crawl website ")
                        if(cleaned_website is not NULL):
                            temp_website = cleaned_website.replace("'","")
                            print("going to crawl: "+temp_website + " - " + row[9].value)
                            print("starting process")
                            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':  'going to crawl: '+temp_website + ' - ' + row[9].value })
                            loginfo = f"data:{json_data}\n\n"
                            webscrape_thread = Thread(target = scrape_website, args =(row[9].value,temp_website,df_durabilitycategories))
                            webscrape_thread.start()

                        # scrape jaarraport
                        print("going to crawl jaarraport")
                        json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':  'going to download and scrape the jaarraport for : ' + row[9].value })
                        loginfo = f"data:{json_data}\n\n"
                        jaarrekening_thread = Thread(target = scrape_jaarrekeningen, args =(row[9].value,))
                        jaarrekening_thread.start()


                        # Wait for jaarraportscraper to be done
                        jaarrekening_thread.join()
                        # Wait for webscraper to be done
                        if(cleaned_website is not NULL):
                            webscrape_thread.join()

                            #scrape_website(row[9].value,cleaned_website,df_durabilitycategories)
                    else:
                        print("kmo with this ID was found")
                        # TODO check if update was selected 

                    json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':  'ID: '+ str(row[0].value) + ',Naam: '+row[1].value + ',Gem: '+row[2].value })#
                #always run loging at the end
                if(json_data is NULL):
                    json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':  'NO json_data was created!' })
                loginfo = f"data:{json_data}\n\n"
                time.sleep(1)

            print("READING STOPED")
        except Exception:
            #log error 
            print(Exception.value)
            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value':'Error during the reading of xcel' })
            loginfo = f"data:{json_data}\n\n"
            readingXcel = False
    # mark the process has ended
    time.sleep(2)
    readingXcel = False
    loginfo = "nothing"

        


def GetxcelDataLogs():
    while True:
        global loginfo
        if(loginfo=="nothing"):
            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': "No process running"})
            yield f"data:{json_data}\n\n"
        elif (loginfo=="error"):
            json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': "error reading excel"})
            yield f"data:{json_data}\n\n"
        else:
            yield loginfo
        time.sleep(1)

def GetxcelDataStarted():
    global readingXcel
    return readingXcel


def fix_hyperlink(string): # =HYPERLINK("http://www.ett.be/","www.ett.be")
    #remove =HYPERLINK("
    fixed_string = string[12:]
    #remove "...
    fixed_string = fixed_string[:fixed_string.find('"')]

    return fixed_string


def split_into_sector_tags(string):
    # remove illegal characters
    string = string.replace("'","")
    string = string.replace('"',"")
    string = string.replace('(',"")
    string = string.replace(')',"")
    string = string.replace('=',"")
    # en van in vervangen door ,
    string = string.replace(" en ",",")
    string = string.replace(" van ",",")
    string = string.replace(" in ",",")
    # split on , 
    strings = string.split(",")
    # clean spaces 
    cleaned_strings = []
    for tag in strings:
        cleaned_strings.append(tag.rstrip().lstrip())
    #return
    return cleaned_strings
