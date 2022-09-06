from cmath import log
import numpy as np

where_sql = ['Naam','Ondernemings nummer','Natuurlijk Kapitaal','Menselijk Kapitaal','Email','Telefoon nummer','WebAdres','Aantal werknemers','B2B']
sector_sql = ['Sector']
adres_sql = ['Adres','Postcode']
municipality_sql = ['Gemente']
bank_sql = ['Omzet','Balanstotaal','Netto Toegevoegde Waarde']
first = True
def translate_search_to_sql(raw_data):
    global where_sql
    global sector_sql
    global adres_sql
    global bank_sql
    global municipality_sql
    global first
    sql_statement = 'SELECT k.ID,k.name,k.email,k.workforce,k.telephone,k.website,k.adressID,k.financeID,k.b2b,k.humancapitalScore,k.naturalcapitalScore FROM scrape.KMO k '
    joins_added = [False,False,False]
    for item in raw_data:
        if((item in sector_sql) and (joins_added[0] is not True)):
           sql_statement+=" INNER JOIN scrape.sectorlist sl ON sl.kmoId = k.ID  INNER JOIN scrape.sector s ON sl.sectorID = s.ID "
           joins_added[0] = True
        if((item in adres_sql or municipality_sql) and (joins_added[1] is not True)):
           sql_statement+=" INNER JOIN scrape.adress a ON k.adressID = a.ID INNER JOIN scrape.municipality m ON m.zipcode = a.zipcode "
           joins_added[1] = True
        if((item in bank_sql) and (joins_added[2] is not True)):
           sql_statement+=" INNER JOIN scrape.finance f ON k.financeID = f.ID "
           joins_added[2] = True
    first = True
    # add all where sql 
    for pos in np.concatenate([where_sql,sector_sql,adres_sql,bank_sql,municipality_sql]):
        if(pos in raw_data):
            if(raw_data[pos]['Type'] == 'Contains'):
                sql_statement+=where_and(pos)
                sql_statement+= " LIKE '%"+raw_data[pos]['input']+"%'"
            if(raw_data[pos]['Type'] == 'Starts with'):
                sql_statement+=where_and(pos)
                sql_statement+= " LIKE '"+raw_data[pos]['input']+"%'"
            if(raw_data[pos]['Type'] == 'Ends with'):
                sql_statement+=where_and(pos)
                sql_statement+= " LIKE '%"+raw_data[pos]['input']+"'"
            if(raw_data[pos]['Type'] == 'Matches'):
                sql_statement+=where_and(pos)
                sql_statement+= "='"+raw_data[pos]['input']+"'"
            if(raw_data[pos]['Type'] == '='):
                sql_statement+=where_and(pos)
                sql_statement+= "="+raw_data[pos]['input']
            if(raw_data[pos]['Type'] == '<='):
                sql_statement+=where_and(pos)
                sql_statement+= "<="+raw_data[pos]['input']
            if(raw_data[pos]['Type'] == '>='):
                sql_statement+=where_and(pos)
                sql_statement+= ">="+raw_data[pos]['input']
            if(raw_data[pos]['Type'] == 'IS'):
                sql_statement+=where_and(pos)
                sql_statement+= "="+string_to_bool(raw_data[pos]['input'])

    print('''{}  limit 100 ;'''.format(sql_statement))
    return  '''{}  limit 100 ;'''.format(sql_statement)
    



def where_and(pos):
    global first
    att = translate_attribute(pos)
    if(first):
        first=False
        return ' WHERE '+pos_to_join_letter(pos)+'.'+att
    else:
        return ' AND '+pos_to_join_letter(pos)+'.'+att+' '

def pos_to_join_letter(pos):
    global sector_sql
    global adres_sql
    global bank_sql
    global municipality_sql
    global human_sql
    global naruur_sql
    if(pos in sector_sql):
        return "s"
    if(pos in adres_sql):
        return "a"
    if(pos in bank_sql):
        return "f"
    if(pos in municipality_sql):   
        return "m"
    return "k"

def translate_order(order):
    switch={
    'Ascending': "ASC",
    'Descending': "DESC",
    } 
    return switch.get(order)

def score_to_number(letter):
    switch={
    'A': "1",
    'B': "2",
    'C': "3",
    }
    return switch.get(letter)

def string_to_bool(string):
    switch={
    'True':  "1",
    'False': "0",
    }
    return switch.get(string)

def translate_attribute(raw_attribute):
    switch={
       'Naam': "name",
       'Menselijk Kapitaal': "humancapitalScore",
       'Natuurlijk Kapitaal': "naturalcapitalScore",
       'Ondernemings nummer': "ID",
       'Email': "email",
       'Telefoon nummer': "telephone",
       'WebAdres': "website",
       'Aantal werknemers': "workforce",
       'B2B': "b2b",
       'Sector': "name",
       'Adres': "street",
       'Postcode': "zipcode",
       'Gemente': "name",
       'Omzet': "turnover",
       'Balanstotaal': "totalAssets",
       'Netto Toegevoegde Waarde': "netValueAdded",
       }
    return switch.get(raw_attribute)