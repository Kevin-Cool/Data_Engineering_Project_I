from asyncio.windows_events import NULL
from distutils.log import debug
import imp
from flask import Flask, render_template, request, url_for, Response, stream_with_context
from xlReader import test,GetxcelDataLogs,GetxcelData,GetxcelDataStarted,fix_hyperlink,split_into_sector_tags
from webScraper import scrape_website
from scoreFunctions import update_kmo_scores,update_sector_scores
from sqlFuncions import translate_search_to_sql
from jaarrekeningen import scrape_jaarrekeningen,read_pdf
from sqlConnection import _MYSQL, _MYSQL_INSERT
import json
import random
import time
from datetime import datetime
import pymysql
import selenium 
import pandas as pd
from sshtunnel import SSHTunnelForwarder

app = Flask(__name__)
# basic sql statements
kmo_all = '''SELECT k.ID,k.name,k.email,k.workforce,k.telephone,k.website,k.adressID,k.financeID,k.b2b,k.humancapitalScore,k.naturalcapitalScore FROM scrape.kmo as k limit 100;'''
# MYSQL returns pandas dataframe


# Routing
@app.route('/sqlTest')
def sqlTest():
    #data = _MYSQL('''SELECT VERSION();''')
    data = _MYSQL('''SELECT * FROM scrape.KMO;''')
    return str(data.iloc[0])

# KMO Overview pages 
@app.route('/KMOOverview')
def KMOOverviewBase():
    db_data_KMO = _MYSQL(kmo_all)
    db_data_KMO.set_index('ID',inplace=True)
    db_data_sector = _MYSQL('''SELECT * FROM scrape.Sector;''')
    db_data_sector.set_index('ID',inplace=True)
    df_scores = _MYSQL('''SELECT * FROM scrape.population_scores; ''')
    df_scores.set_index('ABCD_score',inplace=True)
    #return db_data_KMO.to_json(orient="index",force_ascii=True,index=True)
    return render_template('KMO_overview.html', kmo_data=db_data_KMO.to_json(orient="index",force_ascii=True,index=True), sector_data=db_data_sector.to_json(orient="index",force_ascii=True,index=True), baseurl=request.base_url, ABC_scores = df_scores.to_json(orient="index",force_ascii=True,index=True))
    #return render_template('KMOOverview.html', tables=[db_data.to_html(classes='data')], titles=db_data.columns.values)

# KMO Overview pages 
@app.route('/SectorOverview')
def SectorOverviewBase():
    db_data_sector = _MYSQL('''SELECT * FROM scrape.Sector limit 100;''')
    db_data_sector.set_index('ID',inplace=True)
    df_scores = _MYSQL('''SELECT * FROM scrape.sector_population_scores; ''')
    df_scores.set_index('ABCD_score',inplace=True)
    return render_template('sector_overview.html', sector_data=db_data_sector.to_json(orient="index",force_ascii=True,index=True), baseurl=request.base_url, ABC_scores = df_scores.to_json(orient="index",force_ascii=True,index=True))



# Sector Overview pages

# Get SectorList info
@app.route('/getSectorListInfo/<path:path>')
def GetSectorListByID(path):
    ID = path.replace("%20", " ")
    db_data = _MYSQL('''SELECT * FROM scrape.sectorlist where kmoID = '{}';'''.format(ID))
    return db_data.to_json(orient="index",force_ascii=True,index=True)

# Get location Info
@app.route('/getLocationInfo/<path:path>')
def GetLocationByID(path):
    ID = path.replace("%20", " ")
    db_data = _MYSQL('''SELECT a.ID,a.street,a.zipcode, m.name as municipalityName FROM scrape.adress a inner join scrape.municipality m on m.zipcode = a.zipcode WHERE ID='{}';'''.format(ID))
    return db_data.to_json(orient="index",force_ascii=True,index=True)

# Get Balans info
@app.route('/getBalansInfo/<path:path>')
def GetBalansByID(path):
    ID = path.replace("%20", " ")
    db_data = _MYSQL('''SELECT * FROM scrape.finance WHERE ID='{}';'''.format(ID))
    return db_data.to_json(orient="index",force_ascii=True,index=True)

# Get All Durability Keywords
@app.route('/getAllDurability')
def GetAllDurability():
    df_durabilitycategories = _MYSQL('''SELECT dc.name as "Category",dt.name as "Term",dt.description as "Description",dk.ID as "KeyWordID",dk.name as "KeyWord" FROM scrape.durabilitycategories as dc INNER JOIN scrape.durabilityterms as dt ON dc.name = dt.durabilitycategoriesID INNER JOIN scrape.durabilitykeywords as dk ON dt.name = dk.durabilityterms;''')
    return df_durabilitycategories.to_json(orient="index",force_ascii=True,index=True)

# Get  Durability Keywords of KMO
@app.route('/getDurabilityByID/<path:path>')
def GetDurabilityByID(path):
    ID = path.replace("%20", " ")
    df_durabilitycategories = _MYSQL('''SELECT kd.ID, kd.kmoID,kd.durabilitykeywordID,kd.context,dk.durabilityterms as "Term",dk.name as "Keyword" FROM scrape.kmodurabilityitems kd INNER JOIN scrape.durabilitykeywords dk ON kd.durabilitykeywordID = dk.ID where kd.kmoID = '{}';'''.format(ID))
    return df_durabilitycategories.to_json(orient="index",force_ascii=True,index=True)

# Get  Durability Keywords of KMO
@app.route('/getEmployeesByID/<path:path>')
def getEmployeesByID(path):
    ID = path.replace("%20", " ")
    df_employee = _MYSQL('''SELECT * FROM scrape.kmo_employees where kmo_ID = '{}';'''.format(ID))
    return df_employee.to_json(orient="index",force_ascii=True,index=True)




# save total score in kmo self 
# OR 
#   Later get all numbers and create 4 brake points 
#   create a automatic splitsing of db (perhaps)
#   create the 4 running averages?

# multi select querry
@app.route('/search/KMO', methods = ['GET', 'POST'])
def searchKMOs(): 
    raw_data = request.get_json()
         
    
    df_data_KMO = _MYSQL(translate_search_to_sql(raw_data))
    print(df_data_KMO)
    df_data_KMO.drop_duplicates(subset=['ID'],inplace = True)
    df_data_KMO.set_index('ID',inplace=True)
    # check if need to reorder
    return df_data_KMO.to_json(orient="index",force_ascii=True,index=True)
    #return sql_statement

# scrape urls

@app.route('/ImportFromXcel/StartProgress')
def XcelDatastart():
    if(GetxcelDataStarted() is False):
        GetxcelData()
        return "started"
    else:
        return "Already running"

# update score distributions 

@app.route('/UpdateScore')
def UpdateScore():
    update_kmo_scores()
    update_sector_scores()
    return "done"

@app.route('/GetABCScores')
def GetABCScores():
    df_scores = _MYSQL('''SELECT * FROM scrape.population_scores; ''')
    df_scores.set_index('ABCD_score',inplace=True)
    return df_scores.to_json(orient="index",force_ascii=True,index=True)


# scrape jaarrekeningen
@app.route('/ScrapeALLJaarrekeningen')
def scrapeJaarrekeningen():
    df_kmo_IDs = _MYSQL('''SELECT ID FROM scrape.kmo; ''')
    print(df_kmo_IDs.columns)
    for index,row in df_kmo_IDs.iterrows():
        print(row)
        scrape_jaarrekeningen(row['ID'])
    return "done?"

@app.route('/ScrapeJaarrekeningen/<path:path>')
def scrapeJaarrekening(path):
    ID = path.replace("%20", " ")
    scrape_jaarrekeningen(ID)
    return "done?"
    

# Test Pages

@app.route('/readpdf')
def readpdfTest():
    read_pdf(r"C:\Users\kevin\Documents\scrapedownloads\2021-34800468.pdf","BE0416905901")
    return "done?"


@app.route('/INSERTTEST')
def INSERTTEST():
    _MYSQL_INSERT('''INSERT INTO scrape.municipality (zipcode, name) VALUES (9800,'DEINZE');''')
    df_Data = _MYSQL('''SELECT * FROM scrape.municipality where zipcode = '9800';''')
    return df_Data.to_json(orient="index",force_ascii=True,index=True)


@app.route('/splittest')
def splittest():
    print(split_into_sector_tags("Groothandel in akkerbouwproducten en veevoeders, algemeen assortiment"))
    return "test"

@app.route('/webtest')
def webtest():
    df_durabilitycategories = _MYSQL('''SELECT dc.name as "Category",dt.name as "Term",dt.description as "Description",dk.ID as "KeyWordID",dk.name as "KeyWord" FROM scrape.durabilitycategories as dc INNER JOIN scrape.durabilityterms as dt ON dc.name = dt.durabilitycategoriesID INNER JOIN scrape.durabilitykeywords as dk ON dt.name = dk.durabilityterms;''')
    return scrape_website('BE0453957723','http://www.volckaert.be/',df_durabilitycategories)

@app.route('/substringtest')
def substringtest():
    return "'"+ fix_hyperlink('=HYPERLINK("http://www.vanhoecke.be/";"www.vanhoecke.be")')+"'"

@app.route('/stringtest')
def stringtest():
    test_t = 'rable devices, as well as automotive, Internet of Things, industrial, and connected home applications; and flash-based memory wafers. The company also provides data center devices and solutions comprising enterprise helium hard drives; enterprise SSDs consisting of flash-based SSDs and software solutions for use in enterprise servers, online transactions, data analysis, and other enterprise applications; data center solutions for data storage systems and tiered storage models; and data storage platforms. In addition, it offers client solutions, such as external HDD storage products in mobile and desktop form; client portable SSDs; removable cards that are used in consumer devices comprising mobile phones, tablets, imaging systems, and cameras and smart video systems; universal serial bus flash drives for use in the computing and consumer markets; and wireless drive products used in-field back up of created content, as well as wireless streaming of high-definition movies, photos, music, and documents to tablets, smartphones, and PCs. The company sells its products under the G-Technology, SanDisk, and...'

    test_t = test_t[0:500]+"..."
    return "test "+ str(len(test_t))



                            
@app.route('/SectorOverview')
def SectorOverviewTest():
    db_data = _MYSQL('''SELECT * FROM scrape.Sector;''')
    return render_template('KMOOverview.html', tables=[db_data.to_html(classes='data')], titles=db_data.columns.values)

 
@app.route('/ImportFromXcel')
def ImportFromxl():
    return render_template('ImportFromxl.html', baseurl=request.base_url)

@app.route('/ImportFromXcel/GetProgress')
def XcelData():
    response = Response(stream_with_context(GetxcelDataLogs()), mimetype="text/event-stream")   
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)


   