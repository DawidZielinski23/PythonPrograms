from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import sys

def get_exchange_rate_from_xe(currency):
    url = "https://www.xe.com"

    currency = currency.upper()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='button__BaseButton-sc-1qpsalo-0 haqezJ']")))
    except:
        return -1

    select_from = driver.find_element(By.XPATH, "//input[@id='midmarketFromCurrency']")
    select_from.click()
    WebDriverWait(driver, 1)
    select_from.send_keys(currency)
    WebDriverWait(driver, 1)
    select_from.send_keys(Keys.ENTER)
    WebDriverWait(driver, 2)

    select_to = driver.find_element(By.XPATH, "//input[@id='midmarketToCurrency']")
    select_to.click()
    WebDriverWait(driver, 1)
    select_to.send_keys("PLN")
    WebDriverWait(driver, 1)
    select_to.send_keys(Keys.ENTER)
    WebDriverWait(driver, 2)


    button = driver.find_element(By.XPATH, "//div[@class='currency-converter__SubmitZone-zieln1-3 eIzYlj']/button[@class='button__BaseButton-sc-1qpsalo-0 clGTKJ']")
    if button != None:
        button.click()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[@class='result__BigRate-sc-1bsijpp-1 iGrAod']")))
    except:
        return -1
    WebDriverWait(driver,2)

    value_field = driver.find_element(By.XPATH,"//p[@class='result__BigRate-sc-1bsijpp-1 iGrAod']")

    value_re = re.findall("\d+\.\d+", value_field.text)

    value = float(value_re[0])

    driver.close()

    return value

def get_prize_from_xtb(instrument, code):
    instrument= instrument.upper()

    if(instrument == "STOCK"):
        url = "https://www.xtb.com/pl/cashstocks/"
    elif(instrument == "ETF"):
        url = "https://www.xtb.com/pl/oferta/dostepne-rynki/etf/"
    else:
        print("Wrong instrument")
        return -1

    code = code.lower()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url + code)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='bid']/strong")))
    except:
        return -1

    prize = driver.find_element(By.XPATH, "//span[@id='bid']")

    value = float(prize.text)

    return value

if len(sys.argv) > 1:
    code_list = []
    value_list = []
    error = 0
    try:
        file = open(sys.argv[1], "r")
    except:
        print("Failed to open file " + sys.argv[1])

    lines = file.readlines()

    for line in lines:
        data = line.split()
        if len(data) != 4:
            error = 1
            break

        count = float(data[0])
        instrument = data[1]
        code = data[2]
        currency_code = data[3]

        if currency_code == "PLN":
            currency = 1
        else:
            currency = get_exchange_rate_from_xe(currency_code)

        instrument_prize = get_prize_from_xtb(instrument, code)

        value = float(count) * float(currency) * float(instrument_prize)

        code_list.append(code)
        value_list.append(value)

    if error != 0:
        print("Error!")
    else:
        for i in range(0, len(code_list)):
            print(code_list[i] + ": " + str(round(value_list[i] , 2)) + " PLN")
else:
    print("Please provide filename")