from asyncio.windows_events import NULL
import re
import time
from sqlConnection import _MYSQL, _MYSQL_INSERT

from selenium import webdriver

def scrape_website(kmo_ID,website,durabilitycategories):
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    try:
        #print(durabilitycategories)
        browser = webdriver.Chrome(PATH)
        if(website[0:4] != "http"):
            website = "https://"+website
        browser.get(website)
        # get real base_url
        base_web_url=  get_base_url(browser.current_url)
        #time.sleep(3)
        full_home_page =  browser.find_element_by_xpath("//body")

        nav_pure_html = full_home_page.get_attribute("innerHTML")
        scraped_page_urls = get_all_valid_urls(nav_pure_html,base_web_url)
        print(scraped_page_urls)
        # Check each page for keywords
        temp_keyword_list = []
        for page_url in scraped_page_urls:
            try:
                # get full page
                current_page_url = base_web_url+page_url
                print("crawling to page:"+current_page_url)
                browser.get(current_page_url)  
                time.sleep(1)
                current_page_body =  browser.find_element_by_xpath("//body")
                current_page_html = current_page_body.get_attribute("innerHTML")
                # get every text element: > ... <
                try:
                    inner_elements = re.findall("(?<=>).*?(?=<)",current_page_html)
                    # check the inside of each element for keywords
                    for inner_element in inner_elements:
                        temp_split = inner_element.split('>')
                        last_element = temp_split[-1].rstrip().lstrip()
                        # remove bad characters
                        last_element = last_element.replace("'","")
                        # if string is large enough search for keywords
                        if(len(last_element)>=2):
                            # check if contains keyword 
                            for index, row in durabilitycategories.iterrows():
                                #print("checking vs every keyword")
                                if(str.__contains__(last_element, row['KeyWord'])):
                                    temp_combination = list((row['KeyWordID'],last_element))
                                    temp_keyword_list.append(temp_combination)

                except:
                    print("!!!!!      crawling page failed")

            except:
                print("!!!!!!      getting page failed")

            
        # remove dublicates
        keyword_list_cleaned = []
        for temp_keyword in temp_keyword_list:
            if(temp_keyword not in keyword_list_cleaned):
                keyword_list_cleaned.append(temp_keyword)
        # prepare uniquelist human/natural for scores
        unique_human = []
        unique_natural = []
        # add humancapital/naturalcapital element to DB 
        try:
            for kmo_keyword in keyword_list_cleaned:
                try:
                    # make sure text is not to long
                    if(len(kmo_keyword[1])>512):
                        kmo_keyword[1] = kmo_keyword[1][0:500]+"..."
                    _MYSQL_INSERT('''INSERT INTO scrape.kmodurabilityitems (kmoID, durabilitykeywordID, context) VALUES ('{}', {}, '{}'); '''.format(kmo_ID,kmo_keyword[0],kmo_keyword[1])) 
                    # check if is unique
                    relevant_key = durabilitycategories.loc[durabilitycategories['KeyWordID'] == kmo_keyword[0]]
                    if(relevant_key.iloc[0].Category == "Humancapital"):
                        #check if unique in human
                        unique = True;
                        for human_term in unique_human:
                            if(human_term == relevant_key.iloc[0].Term):
                                unique = False
                        if(unique):
                            unique_human.append(relevant_key.iloc[0].Term)
                    else:
                        #check if unique in nature
                        unique = True;
                        for natural_term in unique_natural:
                            if(natural_term == relevant_key.iloc[0].Term):
                                unique = False
                        if(unique):
                            unique_natural.append(relevant_key.iloc[0].Term)

                except:
                    print("!!!!!!      inner insert failed")
            # add total score to kmo 
            total_human = len(unique_human)
            total_nature = len(unique_natural)
            _MYSQL_INSERT(''' UPDATE scrape.kmo SET humancapitalScore = {human}, naturalcapitalScore = {nature} WHERE  ID = '{ID}';'''.format(human = total_human, nature = total_nature , ID = kmo_ID))
        except Exception as e:
            print("!!!!!!      outer insert failed")
            print("Exception: ", e)
        
        time.sleep(3)
    except Exception as e:
        print("getting website failed")
        print("Exception: ", e)

    
    return "done?"

def get_base_url(url):
    temp_url = url[url.find("www"):]
    url_bits = temp_url.split('/')
    return url[:url.find("www")]+url_bits[0]

def get_all_valid_urls(raw_html,base_webadress):
    # remove http if there
    cleaned_webadress = base_webadress
    if(str.__contains__(base_webadress, "http")):
        cleaned_webadress = base_webadress[base_webadress.find("www"):]
    print("website: "+cleaned_webadress)
    # get all hrefs
    all_href = re.findall("((?<=href=\")(.*)(?=\"))|((?<=href=')(.*)(?='))",raw_html)
    cleaned_hrefs = []
    for href_item in all_href:
        # clean any bad " inport
        temp_href = ""
        if(str.__contains__(href_item[0], '"')):
            temp_split = href_item[0].split('"')
            temp_href = temp_split[0]
        elif(str.__contains__(href_item[0],"'")):
            temp_split = href_item[0].split("'")
            temp_href = temp_split[0]
        else:
           temp_href = href_item[0]
        # skip urls with illegal characters 
        if(not str.__contains__(temp_href, "$") and not str.__contains__(temp_href, "{") and not str.__contains__(temp_href, "mailto")):
            # remove links to external sites 
            if(str.__contains__(temp_href, "www")):
                if(str.__contains__(temp_href, cleaned_webadress)):
                    #remove base url first 
                    temp_href = temp_href.split(cleaned_webadress)[-1]
                    cleaned_hrefs = add_unique_to_list(cleaned_hrefs,temp_href)
            elif(str.__contains__(temp_href, "http")):
                if(str.__contains__(temp_href, base_webadress)):
                    #remove base url first 
                    temp_href = temp_href.split(cleaned_webadress)[-1]
                    cleaned_hrefs = add_unique_to_list(cleaned_hrefs,temp_href)
            else:
                cleaned_hrefs = add_unique_to_list(cleaned_hrefs,temp_href)
        

    return cleaned_hrefs

def add_unique_to_list(list,new_item):
    local_new_item = new_item
    # check if link is missing its /
    if(not str.__contains__(local_new_item, "/")):
        local_new_item = "/"+local_new_item
    new = True
    for list_item in list:
        if(list_item == local_new_item):
            new = False
    if(new):
        list.append(local_new_item)
    return list

