from copy import Error
import json
import time
import os
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from typing import List
from pathlib import Path


# Variables:
#           - Offline Sites list that will store offline sites.
#           - Sites that are available in gov

offline_sites = []
sites = ["http://www.sh.gov.zm/", "http://www.ovp.gov.zm/", "http://www.cabinet.gov.zm/", "http://www.psmd.gov.zm/", "http://www.ago.gov.zm/", "http://www.mod.gov.zm/", "http://www.moha.gov.zm/", "http://www.mofa.gov.zm/", "http://www.mof.gov.zm/", "http://www.moj.gov.zm/", "http://www.mndp.gov.zm/", "http://www.agriculture.gov.zm/", "http://www.mfl.gov.zm/", "http://www.mcti.gov.zm/", "http://www.mmmd.gov.zm/", "http://www.moe.gov.zm/", "http://www.mota.gov.zm/", "http://www.mtc.gov.zm/", "http://www.mws.gov.zm/", "http://www.mhid.gov.zm/", "http://www.mlnr.gov.zm/",
         "http://www.mwdsep.gov.zm/", "http://www.moh.gov.zm/", "http://www.mibs.gov.zm/", "http://www.moge.gov.zm/", "http://www.mohe.gov.zm/", "http://www.mlgh.gov.zm/", "http://www.mlss.gov.zm/", "http://www.mcdsw.gov.zm/", "http://www.gender.gov.zm/", "http://www.myscd.gov.zm/", "http://www.mocta.gov.zm/", "http://www.mngra.gov.zm/", "http://www.cen.gov.zm/", "http://www.cbt.gov.zm/", "http://www.eas.gov.zm/", "http://www.lua.gov.zm/", "http://www.lsk.gov.zm/", "http://www.muc.gov.zm/", "http://www.nws.gov.zm/", "http://www.nor.gov.zm/", "http://www.sou.gov.zm/", "http://www.wes.gov.zm/"]

def init():

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options = options)

    # Make a new folder with todays date - year (%Y), month(%m), and day(%d)
    today = (datetime.datetime.now().strftime("%Y%m%d"))
    todays_photos: Path = Path(today)
    if not todays_photos.exists():
        try:
            os.mkdir(today)
        except OSError as e:
            print(f"Fatal Error, cannot create folder: \n\t{e}")
            os.close()
    check_sites(driver = driver, sites=sites, path=Path(today))

    



def save_screenshot(driver = webdriver.Chrome, file_name: Path = Path('./img.png'), url: str = 'http://sh.gov.zm', include_scrollbar: bool = True) -> None:
    '''
        Saves a screenshot of a webpage given the parameters. Parameters include whether r not to include the 
        scrollbar, path to save the image, and the web driver to use.
    '''
    driver.get(url)
    time.sleep(2)
    padding = 100
    file_name = str(file_name)

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


def check_sites(driver: webdriver.Chrome, sites: List[str], path: Path = Path('./')):
    # Go through the list of sites
    for site in sites:
        try:
            print(f"Getting site: {site}")
            file_name: Path = Path(f"{path}\\{site.split('.')[-3]}.png")
            # driver.save_screenshot(path)
            # Save a snapshot of the site page inside todays folder
            save_screenshot(driver = driver, file_name=file_name, include_scrollbar= False, url=site)
        except Exception as e:
            print(f"Failed to get site: \n\t{e}")
            offline_sites.append(site)
    driver.close()
    # Save the offline sites in a json file
    with open('offline_sites.json', 'w+') as f:
        f.write(json.dumps(offline_sites))

if __name__ == '__main__':
    init()
