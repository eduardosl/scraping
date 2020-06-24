#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import requests
import json
from bs4 import BeautifulSoup


# Cargar datos geográficos

df = pd.read_csv('MX.csv')


# Definir _requests_

def request_stores(lat, lon):
    url = 'https://www.farmaciasguadalajara.com/es/farmaciasguadalajara/ayuda/PDPStoreLocatorResultFGView'
    headers = {'authority': 'www.farmaciasguadalajara.com',
                'dnt': '1',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'origin': 'https://www.farmaciasguadalajara.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.farmaciasguadalajara.com/es/farmaciasguadalajara/ayuda/localizador-de-superfarmacias',
                'accept-language': 'en-US,en;q=0.9,fr;q=0.8,es;q=0.7',
                'cookie': 'userInfo=eyJhbGciOiJIUzUxMiJ9.eyJlbWFpbCI6Imd1ZXN0QGZyYWd1YS5jb20ubXgiLCJ1c2VyTmFtZSI6Ikludml0YWRvIn0.PwnD22gjfb2S6-k_wJWk92fGfko45VyL7f60m9C6bXj-F37bGqNhI2wtT8HIQnlksDUyPBKPodVSEbDNtVzAXQ; CompareItems_10151=; WC_SESSION_ESTABLISHED=true; WC_ACTIVEPOINTER=-24%2C10151; WC_AUTHENTICATION_2505805=2505805%2C3Uekb%2FHdmOQH3vRmlVgL9LgfiihlKI5AoYE7KF2z5uA%3D; FG_PreferedStlocId=715839327; FG_CustomerLocation=20.70434~~-103.40315; FG_ZoneId=232; JSESSIONID=0000MYfF3y_LnSEl4XczQKxbPBh:wcsapp01; WC_PERSISTENT=n4z2EtIm8GqhvrZp7qzVYhkv8TTduGOktt1QS11Uk4I%3D%3B2020-06-23+14%3A44%3A33.683_1592536186236-2556_10151_2505805%2C-24%2CMXN%2C6QIzVCqtYLFxTAR8Ob4KHpjBKQbXww70jVRpgpuB8rmD9D%2B8xNWtdGVxM2evhIGq5ab9P07rvkYhNVVB55DNfA%3D%3D_10151; WC_USERACTIVITY_2505805=2505805%2C10151%2Cnull%2Cnull%2C1592536201172%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C88421994%2CQ8DJvp86RuHqXXdU2X2rja6ESSKEh5ZCynkECcUvgJxJmPhcoWPElBAfZnw2ZaOXuE2j9FKr80SLOsHynGa7HMkmVndu%2BHreSFvyb79Euha2YAN8Ect9ya8HWanQHsQqbmg4XxL%2Bqd%2FLGWgXS%2FFHtqXnhyLC2%2BDWba5KoJh7Fwa0P9ODU34ueNICBdAHsXoaR2S68pUvtXYiDFx2XvDfG6FLp%2FylaL%2FY3zi%2FNpTDv09FFQmHBJYrkP6YO3eQRvt3;'}
    headers['cookie'] +=  'FG_ClientLocationSearch=' + str(lat) + '~' + str(lon)
    raw_data = 'storeId=10151&catalogId=10052&langId=-24&latitude={}&longtitude={}&locality=cp%2005200&paginafgg=&objectId=&requesttype=ajax'.format(lat, lon)

    return requests.post(url, headers=headers, data=raw_data)


# Procesar _requests_

def process(r):
    soup = BeautifulSoup(r.text, 'html.parser')
    if soup.find(id='nearestStoreLength').get('value') == '0':
        return []
    else: 
        x = soup.find_all(id='mapLl')[0];
        return json.loads(x.get('value'))


# Procesar atributos de cada tienda

def process_attributes(s):
    for a in s['Attribute']:
        s[a['displayName']] = a['displayValue']
    s.pop('Attribute')

    s['thumbnail'] = s['Description'][0]['thumbnail']
    s['displayStoreName'] = s['Description'][0]['displayStoreName']
    s.pop('Description')
    
    return s


# Realizar _scraping_

if __name__=="__main__":
	uniqueIDs = []
	out = []
	df_s = df #df[(df['Estado']=='Distrito Federal')]
	df_s = df_s.drop_duplicates(subset=['CP'])
	df_s = df_s.drop_duplicates(subset=['Lat', 'Lon'])
	for i in range(0, len(df_s)):
	    x = df_s.iloc[i]
	    print('Buscando tiendas en C.P. {} ({} de {})'.format(x.CP, i+1, len(df_s)))
	    lat = x.Lat
	    lon = x.Lon
	    r = request_stores(lat, lon)
	    stores = process(r)
	    for s in stores:
	        if s['uniqueID'] not in uniqueIDs:
	            s = process_attributes(s)
	            out.append(s)
	            uniqueIDs.append(s['uniqueID'])


	pd.DataFrame(out).to_csv('sucursales.csv')


"""
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1))         * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

r=request_stores(float(df[df.CP==5200].Lat), float(df[df.CP==5200].Lon))
"""
