from copy import Error
import json
import time
import os
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from typing import List, Set
from pathlib import Path
from urllib.parse import urlparse
import logging as log



# Variables:
#           - Offline Sites list that will store offline sites.
#           - Sites that are available in gov

offline_sites: list = []
sites: list = ["http://www.sh.gov.zm/", "http://www.ovp.gov.zm/", "http://www.cabinet.gov.zm/", "http://www.psmd.gov.zm/", "http://www.ago.gov.zm/", "http://www.mod.gov.zm/", "http://www.moha.gov.zm/", "http://www.mofa.gov.zm/", "http://www.mof.gov.zm/", "http://www.moj.gov.zm/", "http://www.mndp.gov.zm/", "http://www.agriculture.gov.zm/", "http://www.mfl.gov.zm/", "http://www.mcti.gov.zm/", "http://www.mmmd.gov.zm/", "http://www.moe.gov.zm/", "http://www.mota.gov.zm/", "http://www.mtc.gov.zm/", "http://www.mws.gov.zm/", "http://www.mhid.gov.zm/", "http://www.mlnr.gov.zm/",
         "http://www.mwdsep.gov.zm/", "http://www.moh.gov.zm/", "http://www.mibs.gov.zm/", "http://www.moge.gov.zm/", "http://www.mohe.gov.zm/", "http://www.mlgh.gov.zm/", "http://www.mlss.gov.zm/", "http://www.mcdsw.gov.zm/", "http://www.gender.gov.zm/", "http://www.myscd.gov.zm/", "http://www.mocta.gov.zm/", "http://www.mngra.gov.zm/", "http://www.cen.gov.zm/", "http://www.cbt.gov.zm/", "http://www.eas.gov.zm/", "http://www.lua.gov.zm/", "http://www.lsk.gov.zm/", "http://www.muc.gov.zm/", "http://www.nws.gov.zm/", "http://www.nor.gov.zm/", "http://www.sou.gov.zm/", "http://www.wes.gov.zm/"]
visited_pages: Set[str] = set()

def init():

    # make a folder for the screenshots
    screenshots: Path = make_dir(os.getcwd(), "screenshots")

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options = options)


    # Make a new folder with todays date - year (%Y), month(%m), and day(%d)
    today = (datetime.datetime.now().strftime("%Y%m%d"))
    todays_photos: Path = make_dir(screenshots, name=today)        
    check_sites(driver = driver, sites=sites[:2], path=todays_photos)

def make_dir(parent: str, name: str) -> Path:
    '''
     create a new logical subdirectory of parent given directory name and parent
     If the directory exists return it to the caller, if not create a new directory and return it to the caller
    '''
    dir: Path = Path(parent).joinpath(name)
    
    if dir.exists():
        return dir
    try:
        os.mkdir(path=dir)
    except OSError as e:
        log.critical(f"Fatal Error, cannot create folder named {name}: \n\t{e}")
        os.close()
    return dir

    



def save_screenshot(driver = webdriver.Chrome, file_name: Path = Path('./img.png'), url: str = 'http://sh.gov.zm', include_scrollbar: bool = True) -> None:
    '''
        Saves a screenshot of a webpage given the parameters. Parameters include whether r not to include the 
        scrollbar, path to save the image, and the web driver to use.
    '''
    driver.get(url)
    # add the site to set of visited sites
    visited_pages.add(url)
    time.sleep(5)
    padding = 100
    
    file_name = str(check_name(file_name=file_name))
    # print(f'saving pic:\n\t{file_name}')
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.scrollingElement.scrollWidth')
    required_height = driver.execute_script('return document.scrollingElement.scrollHeight')
    required_width = required_width + padding
    required_height = required_height + padding

    driver.set_window_size(required_width, required_height)
    if include_scrollbar:
        driver.save_screenshot(file_name)
    else:
        driver.find_element_by_tag_name('body').screenshot(file_name)
    driver.set_window_size(original_size['width'], original_size['height'])
    return

def check_name(file_name: Path, copy: int = 2) -> str:
    import re
    name = re.sub('[\\\\/:*?\"<>|]*', '', file_name.name)
    file_name = file_name.parent.joinpath(name)
    if file_name.exists():
        file_name = Path(f'{str(file_name)[:-4]}({copy}).PNG')
        if file_name.exists():
            # get the number in the braces, turn it into an int, increment by 1, recurse
            copy = int(str(file_name).split('(')[1][:-5]) + 1
            file_name = Path(f'{str(file_name)[:-4]}({copy}).PNG')
            return check_name(file_name=file_name, copy=copy)
    
    return file_name

def get_links(path: Path, driver: webdriver.Chrome):
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    # get all links in the page by getting anchor tags then their hrefs
    links: List[str] = [x.get_attribute('href') for x in driver.find_elements_by_tag_name("a")] 
    # traverse set of anchor tags
    
    for ref in links:
        if ref is not None:
            # if the link has been visited before, skip to next link (interation)
            if ref in visited_pages:
                continue
            if ref.endswith('#'):
                pass 
            name = ref.split('/')[-1]
            photo_name: Path = path.joinpath(f'{name}.png')
            save_screenshot(driver=driver, file_name=photo_name, url= ref, include_scrollbar= False)
            # Recursively traverse the site for all anchor tags leading to a link
            #get_links(path=path, driver=driver)
    
             

def check_site(url: str, path: Path, driver: webdriver.Chrome):
    host_name: str = urlparse(url).hostname
    dir: Path = make_dir(parent=path, name=host_name)
    home_pic = dir.joinpath('home.png')
    save_screenshot(driver=driver, file_name= home_pic, url=url, include_scrollbar=False)
    get_links(path=dir, driver=driver)
    



def check_sites(driver: webdriver.Chrome, sites: List[str], path: Path):
    # Go through the list of sites
    for site in sites:
        try:
            print(f"Getting site: {site}")
            file_name: Path = Path(f"{path}\\{urlparse(site).hostname}.png")
            # driver.save_screenshot(path)
            # Save a snapshot of the site page inside todays folder
            check_site(url=site, path=path, driver = driver)
        except Exception as e:
            print(f"Failed to get site: {site} \n\t{e}")
            # TODO: log the error properly here
            # log.error()
            offline_sites.append(site)
            raise e
    driver.close()
    # Save the offline sites in a json file
    with open('offline_sites.json', 'w+') as f:
        f.write(json.dumps(offline_sites))

if __name__ == '__main__':
    init()
