##### DOESNT WORK ANYMORE AFTER YELP UPDATED THEIR WEBPAGE

import requests
from bs4 import BeautifulSoup

import pandas as pd
import time


uri_u = 'https://www.yelp.ca/search?find_desc=&find_loc=Vancouver%2C%20BC&l=p%3ABC%3AVancouver%3A%3A{}&start='

# Need to split because Yelp website breaks after page 100
areas = []
areas.append('Ambleside')
areas.append('Arbutus_Ridge')
areas.append('Ambleside')
areas.append('Arbutus_Ridge')
areas.append('Burnaby_Heights')
areas.append('Central_Lonsdale')
areas.append('Champlain_Heights')
areas.append('Chinatown')
areas.append('Coal_Harbour')
areas.append('Deep_Cove')
areas.append('Dunbar-Southlands')
areas.append('Dundarave')
areas.append('Edgemont_Village')
areas.append('Fairview_Slopes')
areas.append('Fraserview')
areas.append('Downtown')
areas.append('Downtown_Eastside')
areas.append('Gastown')
areas.append('Golden_Village')
areas.append('Grandview-Woodlands')
areas.append('Granville_Entertainment_District')
areas.append('Granville_Island')
areas.append('False_Creek')
areas.append('Hastings-Sunrise')
areas.append('Horseshoe_Bay')
areas.append('Kensington-Cedar_Cottage')
areas.append('Kerrisdale')
areas.append('Killarney')
areas.append('Kitsilano')
areas.append('Lower_Lonsdale')
areas.append('Lynn_Valley')
areas.append('Marpole')
areas.append('Metrotown')
areas.append('Mount_Pleasant')
areas.append('Oakridge')
areas.append('Point_Grey')
areas.append('Punjabi_Market')
areas.append('Renfrew-Collingwood')
areas.append('Riley_Park')
areas.append('SFU')
areas.append('Shaughnessy')
areas.append('South_Cambie')
areas.append('South_Granville')
areas.append('Steveston')
areas.append('Strathcona')
areas.append('Sunset')
areas.append('The_Drive')
areas.append('UBC')
areas.append('West_End')
areas.append('YVR')
areas.append('Yaletown')


def GetValue(string, start, end=None):
    tmp = string
    try:
        if end is None:
            return tmp.split(start)[1]
        else:
            return tmp.split(start)[1].split(end)[0]
    except:
        return 'Error'

s = requests.session()

for area in areas:
    filename = area
    uri = uri_u.format(area)
    df = pd.DataFrame(columns=['rid','rname','reviewCount','review','address','neighborhood','price','link','cuisines'])

    i = 0
    while True:
        print(i)

        newUri = uri + str(i*10)
        r = s.get(newUri,verify=False)
        page = BeautifulSoup(r.content,'html.parser')

        if str(page).find('Did one of our links take you here? Please tell us.') >= 0:
            print("e1")
            break

        restaurants = page.findAll("li",{"class":"domtags--li__373c0__3TKyB list-item__373c0__M7vhU"})
        for res in restaurants:
            html = str(res)
            # Not all were restaurants. Check if it was a restaurant tag
            tmp = html.find('<h3 class="lemon--h3__373c0__5Q5tF heading--h3__373c0__1n4Of alternate__373c0__1uacp">')
            if tmp >= 0:
                dr = {}
                # Restaurant ID
                dr['rid'] = GetValue(html,'<h3 class="lemon--h3__373c0__5Q5tF heading--h3__373c0__1n4Of alternate__373c0__1uacp">','<')

                # Restaurant Name
                tmp = GetValue(html,'<a class="lemon--a__373c0__1_OnJ link__373c0__29943 link-color--blue-dark__373c0__1mhJo link-size--inherit__373c0__2JXk5"')
                dr['rname'] = GetValue(tmp, '>','<')

                # Review Count
                dr['reviewCount'] = GetValue(html,'<span class="lemon--span__373c0__1xR0D text__373c0__2pB8f reviewCount__373c0__2r4xT text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_">', '<')

                # Review (Rating)
                try:
                    tmp = html.split('star rating')[0]
                    tmp = tmp[tmp.rfind('aria-label="'):].split('"')[1]
                    dr['review'] = tmp
                except:
                    dr['review'] = 'Error'

                # Price ($)
                tmp = GetValue(html,'priceRange')
                dr['price'] = GetValue(tmp,  '>', '<')

                # Address
                dr['address'] = GetValue(html,'<span class="domtags--span__373c0__1VGzF">','<')

                # Neighborhood
                tmp = GetValue(html,'<div class="lemon--div__373c0__6Tkil u-space-t1 border-color--default__373c0__2oFDT">')
                dr['neighborhood'] = GetValue(tmp,'<div class="lemon--div__373c0__6Tkil border-color--default__373c0__2oFDT">','<')

                # Cuisines
                lst = []
                cuisines = res.findAll('a',{'class':'lemon--a__373c0__1_OnJ link__373c0__29943 link-color--inherit__373c0__15ymx link-size--default__373c0__1skgq'})
                for c in cuisines:
                    tmp = GetValue(str(c),'>','<')
                    lst.append(tmp)
                dr['cuisines'] = lst

                # Link
                tmp = GetValue(html,'<a class="lemon--a__373c0__1_OnJ link__373c0__29943 link-color--blue-dark__373c0__1mhJo link-size--inherit__373c0__2JXk5"')
                dr['link'] = GetValue(tmp,'href="','"')

                df = df.append(dr,ignore_index=True)


        i += 1
        if str(page).find('<span class="lemon--span__373c0__1xR0D text__373c0__2pB8f text-color--inherit__373c0__w_15m text-align--left__373c0__2pnx_">Next</span>') >= 0:
            time.sleep(10)
            pass
        else:
            break


    df.to_csv(filename + '.csv')
