from selenium import webdriver
import time
import pandas as pd
import numpy as np

# Maquette lets you export the url of a certain view, so you can zoom in and use multiple views 
# You can also run multiple instances of this tool in parallel, each scanning a different area
URLS = ['http://3d.ville-fribourg.ch/?o=eyJ2ZGYtbW50IjoiZmFsc2UiLCJ2ZGYtYmF0IjoidHJ1ZSIsInZkZi1iYXQtcHJvaiI6ImZhbHNlIiwidmRmLXZlZyI6ImZhbHNlIiwidmRmLW9hIjoiZmFsc2UiLCJ2ZGYtYXNzIjoiZmFsc2UiLCJ0dCI6ImZhbHNlIiwic3VuIjoiZmFsc2UiLCJ4IjoiNDM0MjE0NSIsInkiOiI1NDU1ODEiLCJ6IjoiNDYzMTEzMiIsImgiOiI2LjI4IiwicCI6Ii0xLjU3IiwiciI6IjAifQ%3D%3D']

# You need chromedriver.exe either in a known folder or in path variables
CHROME_FOLDER = r"...\Chromedriver\chromedriver"

# Empty lists to collect the data
identifiers = []
egids = []
surfaces = []
volumes = []
starts = []
ends = []
altitudes_1 = []
altitudes_2 = []
altitudes_3 = []
users = []

# Start fullscreen
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
#options.add_argument("--headless")
#options.add_argument("disable-gpu")


# Start Chrome
# IMPORTANT: when the window opens you can minimize it, but don't resize it!
driver = webdriver.Chrome(CHROME_FOLDER, options=options)

for url in  URLS:
    # Open the page and wait a bit
    driver.get(url)
    time.sleep(30)
    
    # Look for the upper-leftmost item which in our case is the terrain toggle button
    # Note that with Selenium you can coordinate click only relatively to an element
    element = driver.find_element_by_id('vdf-mnt')
    
    # Look for the iframe element
    iframe = driver.find_elements_by_tag_name('iframe')[0]
    
    # i = coordinated in x (pixels)
    for i in range(20, 1460, 5): #20, 1520, 4
        
        # j = coordinated in y (pixels)
        for j in range(40, 700, 5): #40, 700, 4
            # Click
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(element, i, j)
            action.click()
            action.perform()
            
            # Switch to the iframe items
            driver.switch_to.frame(iframe)
            
            # Look for div in the html of the iframe and check if it's empty
            text = driver.find_element_by_xpath("//div")

            if text.text != '':
                
                # split the text found in the html
                text_splitted = text.text.split()
                
                # Some buildings don't have an egid
                if 'ID' in text_splitted:
                    
                    # Do some string comprehension and store the infos in the lists
                    identifier = text_splitted[text_splitted.index('ID') + 1]
                    try:
                        egid = text_splitted[text_splitted.index('EGID') + 1]
                    except:
                        egid = np.NaN
                    try:
                        surface = text_splitted[text_splitted.index('sol') + 1]
                    except:
                        surface = np.NaN
                    try:
                        volume = text_splitted[text_splitted.index('(approx.!)') + 1]
                    except:
                        volume = np.NaN
                    try:
                        start = text_splitted[text_splitted.index('(début') + 2]
                    except:
                        start = np.NaN
                    try:
                        end = text_splitted[text_splitted.index('(début') + 8]
                    except: end = np.NaN
                    try:
                        alt1 = text_splitted[text_splitted.index("l'entrée") + 1]
                    except:
                        alt1 = np.NaN
                    try:
                        alt2 = text_splitted[text_splitted.index('corniche') + 1]
                    except:
                        alt2 = np.NaN
                    try:
                        alt3 = text_splitted[text_splitted.index('toit') + 1]
                    except:
                        alt3 = np.NaN
                    try:
                        user = text_splitted[text_splitted.index('bâtiment') + 1]
                    except:
                        user = np.NaN
                    print(egid)
                    if identifier not in identifiers:
                        identifiers.append(identifier)
                        egids.append(egid)
                        surfaces.append(surface)
                        volumes.append(volume)
                        starts.append(start)
                        ends.append(end)
                        altitudes_1.append(alt1)
                        altitudes_2.append(alt2)
                        altitudes_3.append(alt3)
                        users.append(user)
            # Close the frame by clicking in a neutral point
            driver.switch_to.default_content()
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(element, 120, 140)
            action.click()
            action.perform()
        print(i)
        

        
# Create a df with the data        
df = pd.DataFrame(list(zip(identifiers, egids, surfaces, volumes, starts, ends, altitudes_1, altitudes_2, altitudes_3, users)), 
               columns =['ID', 'Egid', 'Surface', 'Volume', 'Année de constr. (début travaux)', 'Année de constr. (fin travaux)',
                         "Altitude de l'entrée",'Altitude de la corniche','Altitude au faîte de toit', 'Genre de bâtiment']) 

# Numbers shouldn't be strings
df[['Egid', 'Surface', 'Volume', 'Année de constr. (début travaux)', 'Année de constr. (fin travaux)',
    "Altitude de l'entrée",'Altitude de la corniche','Altitude au faîte de toit']] = df[['Egid', 'Surface', 'Volume', 'Année de constr. (début travaux)', 'Année de constr. (fin travaux)',
    "Altitude de l'entrée",'Altitude de la corniche','Altitude au faîte de toit']].apply(lambda x: pd.to_numeric(x, errors='coerce'))

# Calc height
df['height'] = df['Volume'] / df['Surface']

# Save
df.to_csv('db_maquette.csv')