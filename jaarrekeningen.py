from asyncio.windows_events import NULL
import json
from multiprocessing.connection import wait
from operator import truediv
from pickle import NONE, TRUE
from pydoc import describe
import random
import string
import re
import time
from datetime import datetime
from traceback import print_tb
from warnings import catch_warnings
from openpyxl import Workbook, load_workbook
from sqlConnection import _MYSQL, _MYSQL_INSERT
from Classes import Humancapital,Naturalcapital
import pymysql

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import requests

import os

from PyPDF2 import PdfReader


def scrape_jaarrekeningen(kmo_ID):
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    print("kmo_ID :"+kmo_ID)
    # make sure download folder is empty
    download_folderpath = r"C:\Users\kevin\Documents\scrapedownloads"
    try:
        filelist = [ f for f in os.listdir(download_folderpath) if f.endswith(".pdf") ]
        for f in filelist:
            os.remove(os.path.join(download_folderpath, f))

    except Exception as e:
        print("!!!!!!      Deleting all file from download folder")
        print("Exception: ", e)

    # set download folder 
    # C:\Users\kevin\Documents\scrapedownloads
    try:
        chr_profile = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : download_folderpath}
        chr_profile.add_experimental_option("prefs",prefs)
    except Exception as e:
        print("!!!!!!      set download location failed")
        print("Exception: ", e)
    
    # goto to website and downlaod PDF
    try:
        browser = webdriver.Chrome(PATH,options=chr_profile)
        browser.get("https://consult.cbso.nbb.be/consult-enterprise/{}".format(kmo_ID[2:]))  
        PDF_download_button = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/main/div/app-search-result/div/div[2]/app-deposit-list/div/div[3]/app-deposit-item[2]/div/div[5]/app-download-deposit-pdf-button/button")) #This is a dummy element
            )

        PDF_download_button.click()

        time.sleep(3) # wait to be sure download is done
        #time.sleep(500)
        #response = requests.get("https://ws.cbso.nbb.be/authentic/legalEntity/{}/references".format("0416905901"),
        #    headers={
        #        #"X-RapidAPI-Host": "alexnormand-dino-ipsum.p.rapidapi.com",
        #        "X-Request-Id": "1c55dcd8-2fbc-9523-fc23-9655c35e2e3f",
        #        "NBB-CBSO-Subscription-Key": "b18466d5a2a540778375d973b3f3dd71",
        #        "Accept": "application/json"
        #    }
        #)
        #print (type(response.json()))
        #print(response.json())

    except Exception as e:
        print("!!!!!!      open website failed")
        print("Exception: ", e)
    
    # open wat should be the only pdf 
    try:
        # get all pdf's
        filelist = [ f for f in os.listdir(download_folderpath) if f.endswith(".pdf") ]
        if(len(filelist)==1):
            print("only one pdf")
            print(filelist[0])
            read_pdf(os.path.join(download_folderpath, filelist[0]),kmo_ID)
        else:
            print("No pdf's found / to more than one pdf found")
            
    except Exception as e:
        print("!!!!!!      FINDING PDF FAILED")
        print("Exception: ", e)

def read_pdf(pdf_path,kmo_ID):
    print(pdf_path)
    reader = PdfReader(pdf_path)# r"C:/Users/kevin/Downloads/2021-03500408.pdf"
    number_of_pages = len(reader.pages)
    for page_nr in range(number_of_pages):
        print("page: " + str(page_nr))
        page = reader.pages[page_nr]
        text = page.extract_text()
        if(str.__contains__(text, "Volgens het geslacht en het studieniveau")):
            print("test contains")
            #print(text)
            lines = text.split("\n")
            print(lines)
            # get index for start
            start_index = 0
            for index, line in enumerate(lines):
                if(str.__contains__(line, "Aantal werknemers")):
                    start_index = index
            try:
                #print("Aantal werknemers:")
                #print(lines[start_index])
                temp_employee_info = split_string_to_categories(lines[start_index])#   Aantal werknemers 
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Aantal werknemers",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+7])#   Mannen 
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Aantal mannen",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+8])#       lager onderwijs
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Mannen met lager onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+9])#       secundair onderwijs 
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Mannen met secundair onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+10])#       hoger niet-universitair onderwijs
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Mannen met hoger niet-universitair onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+11])#       universitair onderwijs
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Mannen met universitair onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+12])#   Vrouwen 
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Aantal vrouwen",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+13])#       lager onderwijs
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Vrouwen, lager onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+14])#       secundair onderwijs 
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Vrouwen met secundair onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+15])#       hoger niet-universitair onderwijs
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Vrouwen met hoger niet-universitair onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+16])#       universitair onderwijs
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "Vrouwen met universitair onderwijs",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+18])#       Directiepersoneel
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "beroepscategorie, Directiepersoneel",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+19])#       Bedienden
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "beroepscategorie, Bedienden",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+20])#       Arbeiders
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "beroepscategorie, Arbeiders",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))
                temp_employee_info = split_string_to_categories(lines[start_index+21])#       Andere
                _MYSQL_INSERT('''INSERT INTO scrape.kmo_employees (kmo_ID, columnText, fulltime, parttime, total) VALUES ('{kmo_ID}', '{columnText}', '{fulltime}', '{parttime}', '{total}');'''.format(
                    kmo_ID = kmo_ID,
                    columnText = "beroepscategorie, Andere",
                    fulltime = temp_employee_info[0],
                    parttime = temp_employee_info[1],
                    total = temp_employee_info[2]
                ))

            except Exception as e:
                print("!!!!!!      Insert employee info into DB failed ")
                print("Exception: ", e)

           
            # info to get           // Voltijds 2. Deeltijds 3. Totaal i
            
            # n voltijdse equivalenten
            #   Aantal werknemers  #split_string_to_categories("Aantal werknemers",text)
            #   Mannen 
            #       lager onderwijs
            #       secundair onderwijs 
            #       hoger niet-universitair onderwijs
            #       universitair onderwijs
            #   Vrouwen 
            #       lager onderwijs
            #       secundair onderwijs 
            #       hoger niet-universitair onderwijs
            #       universitair onderwijs
            #   Volgens de beroepscategorie
            #       Directiepersoneel
            #       Bedienden
            #       Arbeiders
            #       Andere

        #if(str.__contains__(text, "Omzet")):
            # turnover  VASTE ACTIVA 
            # totalAssets   TOTAAL VAN DE ACTIVA
            # netValueAdded Vorderingen op ten hoogste één jaar

    #print(text)

def split_string_to_categories(raw_line):
    raw_line = raw_line.replace(",",".")
    splited_line = raw_line.split(" ")
    if(is_number(splited_line[-1]) and is_number(splited_line[-2]) and is_number(splited_line[-3]) and is_number(splited_line[-4]) and not is_number(splited_line[-5])):
        # last 3 items where numbers
        return [float(splited_line[-3]),float(splited_line[-2]),float(splited_line[-1])]
    elif(is_number(splited_line[-1]) and is_number(splited_line[-2]) and not is_number(splited_line[-4])):
        if(splited_line[-1] == splited_line[-2]):
            # the last 2 items where numbers
            return [float(splited_line[-2]),0,float(splited_line[-1])] 
        else:
            return [0,float(splited_line[-2]),float(splited_line[-1])] 
    else:
        return [0,0,0]

def is_number(n):
    try:
        float(n) 
    except ValueError:
        return False
    return True


# secundair onderwijs 1201 84 9 90,9