from asyncio.windows_events import NULL
from sqlConnection import _MYSQL, _MYSQL_INSERT


def update_kmo_scores():
    print("started update scores process")
    # get all scores 
    df_all_scores = _MYSQL(''' SELECT humancapitalScore,naturalcapitalScore, (humancapitalScore+naturalcapitalScore) as "Total_score" FROM scrape.kmo where humancapitalScore IS NOT NULL AND naturalcapitalScore IS NOT NULL; ''')
    # get breakepoints 
    print(df_all_scores.describe())
    described = df_all_scores.describe()
    # A
    print("A:") # if above :
    print(described.iloc[6])
    # B
    print("B:") # if above :
    print(described.iloc[5])
    # C 
    print("C:") # if above :
    print(described.iloc[4])
    # save breakpoints
    _MYSQL_INSERT(''' TRUNCATE scrape.population_scores ''')
    # A
    _MYSQL_INSERT(''' INSERT INTO scrape.population_scores (ABCD_score, HumancapitalScore, NaturalcapitalScore, TotalScore) VALUES ('A', {}, {}, {});'''.format(described.iloc[6].humancapitalScore,described.iloc[6].naturalcapitalScore,described.iloc[6].Total_score))
    # B
    _MYSQL_INSERT(''' INSERT INTO scrape.population_scores (ABCD_score, HumancapitalScore, NaturalcapitalScore, TotalScore) VALUES ('B', {}, {}, {});'''.format(described.iloc[5].humancapitalScore,described.iloc[5].naturalcapitalScore,described.iloc[5].Total_score))
    # C
    _MYSQL_INSERT(''' INSERT INTO scrape.population_scores (ABCD_score, HumancapitalScore, NaturalcapitalScore, TotalScore) VALUES ('C', {}, {}, {});'''.format(described.iloc[4].humancapitalScore,described.iloc[4].naturalcapitalScore,described.iloc[4].Total_score))



def update_sector_scores():
    print("started update scores process")
    # get all scores 
    df_all_scores = _MYSQL(''' SELECT sectorID,count(Distinct kmoID) as "count",sum(k.humancapitalScore)/count(Distinct kmoID) as "humancapitalScore",sum(k.naturalcapitalScore)/count(Distinct kmoID) as "naturalcapitalScore",(sum(k.humancapitalScore)+sum(k.naturalcapitalScore))/count(Distinct kmoID) as "Total_score"  FROM scrape.sectorlist as sl INNER JOIN scrape.kmo k ON k.ID = kmoID where k.naturalcapitalScore IS NOT NULL AND k.humancapitalScore IS NOT NULL GROUP BY sectorID;''')
    # get breakepoints 
    print(df_all_scores.describe())
    described = df_all_scores.describe()
    # A
    print("A:") # if above :
    print(described.iloc[6])
    # B
    print("B:") # if above :
    print(described.iloc[5])
    # C 
    print("C:") # if above :
    print(described.iloc[4])
    # save breakpoints
    _MYSQL_INSERT(''' TRUNCATE scrape.sector_population_scores ''')
    # A
    _MYSQL_INSERT(''' INSERT INTO scrape.sector_population_scores (ABCD_score, HumancapitalScore, NaturalcapitalScore, TotalScore) VALUES ('A', {}, {}, {});'''.format(described.iloc[6].humancapitalScore,described.iloc[6].naturalcapitalScore,described.iloc[6].Total_score))
    # B
    _MYSQL_INSERT(''' INSERT INTO scrape.sector_population_scores (ABCD_score, HumancapitalScore, NaturalcapitalScore, TotalScore) VALUES ('B', {}, {}, {});'''.format(described.iloc[5].humancapitalScore,described.iloc[5].naturalcapitalScore,described.iloc[5].Total_score))
    # C
    _MYSQL_INSERT(''' INSERT INTO scrape.sector_population_scores (ABCD_score, HumancapitalScore, NaturalcapitalScore, TotalScore) VALUES ('C', {}, {}, {});'''.format(described.iloc[4].humancapitalScore,described.iloc[4].naturalcapitalScore,described.iloc[4].Total_score))
    # add scores to sectors 
    for column_name, row in df_all_scores.iterrows():
        print(''' UPDATE scrape.sector SET humancapitalScore = {}, naturalcapitalScore = {} WHERE (ID = {});'''.format(row.humancapitalScore,row.naturalcapitalScore,row.sectorID))
        _MYSQL_INSERT(''' UPDATE scrape.sector SET humancapitalScore = {}, naturalcapitalScore = {} WHERE (ID = {});'''.format(row.humancapitalScore,row.naturalcapitalScore,row.sectorID))




