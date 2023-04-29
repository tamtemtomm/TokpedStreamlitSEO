import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import base64

from selenium import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

import json
import time
import re
from selenium.webdriver.common.by import By

def scrape_data(prompt, pagestop) :
    links = []
    page = 0
    url = 'https://www.tokopedia.com/'
    search = prompt
    proxy = 'proxy-server=106.122.8.54:3128'
    chromeuser = r'--user-data-dir=C:\Users\HP G7\AppData\Local\Google\Chrome\User Data\Default'

    options = uc.ChromeOptions()
    options.add_argument(proxy)
    options.add_argument(chromeuser)

    driver = uc.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//input[@placeholder="Cari di Tokopedia"]').send_keys(search + Keys.RETURN)

    while(page<pagestop) :
        print(f'Scrape links di page ke-{page+1}')
        time.sleep(1)
        driver.execute_script('window.scrollTo(0, 3000)')
        time.sleep(1)
        driver.execute_script('window.scrollTo(0, 1500)')
        time.sleep(1)
        driver.execute_script('window.scrollTo(0, 4500)')
        time.sleep(2)

        content = driver.find_elements(By.XPATH, "//a[@class='pcv3__info-content css-gwkf0u']")
        for c in content: 
            if c.get_attribute('href').split('/')[1] != 'promo':
                links.append(c.get_attribute('href'))
            
        driver.execute_script('window.scrollTo(0, 5000)')
        driver.find_element(By.XPATH, "(//button/*[name()='svg'])[last()]").click()
        page += 1
    
    print('------------------------------------')
    print(f'Berhasil mendapatkan {len(links)} link')
    print('------------------------------------')

    products = [dict() for x in range(len(links))]

    i = 0
    for link in links :
        print(f'Scrape produk ke-{i+1}')
        driver.get(link)
        time.sleep(1)
        driver.execute_script('window.scrollTo(0, 540)')
        time.sleep(1)
        
        try : 
            products[i]['name'] = driver.find_element(By.XPATH, '//h1').text
        except : 
            products[i]['name'] = '-'
        
        try : 
            products[i]['sold'] = driver.find_element(By.XPATH, "//p[@data-testid='lblPDPDetailProductSoldCounter']").text
        except: 
            products[i]['sold'] = '-'
        
        try : 
            products[i]['rating'] = driver.find_element(By.XPATH, "//span[@data-testid='lblPDPDetailProductRatingNumber']").text
        except: 
            products[i]['rating'] = '-'
        
        try : 
            products[i]['price'] = driver.find_element(By.XPATH, "//div[@data-testid='lblPDPDetailProductPrice']").text
        except: 
            products[i]['price'] = '-'
        
        try : 
            products[i]['city'] = driver.find_element(By.XPATH, "//h2[@class='css-1pd07ge-unf-heading e1qvo2ff2']/b").text
        except : 
            products[i]['city'] = '-'
        i+=1
    
    driver.close()

    df = pd.DataFrame(products)
    df = df[df.name!='Access Denied']
    df = df[df.name!='-']
    
    print('------------------------------------')
    print(f'Berhasil mendapatkan {len(df)} data')
    print('------------------------------------')
    print(f'Memproses data...')
    
    # Data Engineer
    df['city'] = df['city'].apply(lambda x : x if x!='-' else np.nan)
    df['price'] = df['price'].apply(lambda x : int(x[2:].replace('.','')) if x!='-' else np.nan)
    df['rating'] = df['rating'].apply(lambda x : float(x) if x!='-' else np.nan)
    df['sold'] = df['sold'].apply(lambda x : ' '.join(str(x).split(' ')[1:]) if x!='-' else np.nan)
    df['sold'] = df['sold'].apply(lambda x: int(str(x).split()[0])*1000 if str(x)[-3:] == 'rb+' else x)
    df['sold'] = df['sold'].apply(lambda x: int(str(x)[:-1]) if str(x)[-1] == '+' else x)
    df['sold'] = df['sold'].apply(lambda x: int(x) if str(x).isnumeric() else x)
    df = df[df.sold!='barang berhasil terjual']
    
    
    df.to_csv(f'{prompt}product.csv')
    
    print('------------------------------------')
    print(f'Berhasil memproses data!')
    
    return df

def stream_app(df):
    print('------------------------------------')
    print(f'Memulai Streamlit...')
    
    st.title('Make a Simple Stats from Tokopedia Search')
    st.markdown("""
    * **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
    * **Data source:** Live Scraping using Selenium.
    """)
    st.dataframe(df)

def main():
    prompt = input("Masukkan prompt : ")
    page = input("Masukkan page : ")
    df = scrape_data(prompt, int(page))
    stream_app(df)
    
    
if __name__ == '__main__':
    main()