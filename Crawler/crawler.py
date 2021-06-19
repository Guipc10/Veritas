from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time
import json

def delete_cache():
    driver.execute_script("window.open('');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    driver.get('chrome://settings/clearBrowserData') # for old chromedriver versions use cleardriverData
    time.sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3) # send right combination
    actions.perform()
    time.sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 4 + Keys.ENTER) # confirm
    actions.perform()
    time.sleep(5) # wait some time to finish
    driver.close() # close this tab
    driver.switch_to.window(driver.window_handles[0]) # switch back

def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)
#Load JSON file
f = open("/home/guilherme/Unicamp/IC_2021/Downloads/test_jsg.json")
data = json.load(f)

#For each case

PATH = "/home/guilherme/Unicamp/IC_2021/Crawler/chromedriver"

for case in data:
    link = "https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao="+case["cdacordao"]+"&cdForo=0"
    print(link)
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    print(userAgent)
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument("start-maximized")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options, executable_path=PATH)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    set_viewport_size(driver,800,600)
    delete_cache()
    driver.get(link)
    driver.delete_all_cookies()
    driver.implicitly_wait(1)
    recaptcha = driver.find_elements_by_id("uuidCaptcha")
    if (len(recaptcha)>0):
        #There is captcha
        print("tem captcha")
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
    time.sleep(20)
    print("fechou")
    driver.quit()
# search = driver.find_element_by_id("iddadosConsulta.pesquisaLivre")
# search.clear()
# search.send_keys("?")
# search.send_keys(Keys.RETURN)
#
#
# results_table = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"divDadosResultado")))
# for result in results_table.find_elements_by_class_name("fundocinza1"):
#     target = WebDriverWait(result,10).until(EC.presence_of_element_located((By.CLASS_NAME,"fonteNegrito")))
#     #result.find_element_by_class_name("fonteNegrito")
#     target.click()
#
#     handles = driver.window_handles
#     size = len(handles)
#     print("size e " ,size)
#     parent_handle = driver.current_window_handle
#
#     for x in range(size):
#         if handles[x]!=parent_handle:
#             driver.switch_to_window(handles[x])
#             print(driver.title)
#             time.sleep(2)
#             driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[3]/div/div[1]/div[2]/button[5][@id='download']").click()
#             #div_conteudo = driver.find_element_by_id("div-conteudo")
#             #div_conteudo.find_element_by_id("download").click()
#             driver.close()
#     driver.switch_to_window(parent_handle)
#
#
# print("erroooo")
