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
    xpath_button = "//button[@class='button__BaseButton-sc-1qpsalo-0 haqezJ']"
    xpath_input_from = "//input[@id='midmarketFromCurrency']"
    xpath_input_to = "//input[@id='midmarketToCurrency']"
    xpath_button_convert = "//div[@class='currency-converter__SubmitZone-zieln1-3 eIzYlj']/button[@class='button__BaseButton-sc-1qpsalo-0 clGTKJ']"
    xpath_result = "//p[@class='result__BigRate-sc-1bsijpp-1 iGrAod']"

    currency = currency.upper()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath_button)))
    except:
        return -1

    select_from = driver.find_element(By.XPATH, xpath_input_from)
    try:
        select_from.click()
    except:
        return -1
    WebDriverWait(driver, 2)
    select_from.send_keys(currency)
    WebDriverWait(driver, 2)
    select_from.send_keys(Keys.ENTER)
    WebDriverWait(driver, 5)

    select_to = driver.find_element(By.XPATH, xpath_input_to)
    select_to.click()
    WebDriverWait(driver, 2)
    select_to.send_keys("PLN")
    WebDriverWait(driver, 2)
    select_to.send_keys(Keys.ENTER)
    WebDriverWait(driver, 5)


    button = driver.find_element(By.XPATH, xpath_button_convert)
    if button != None:
        button.click()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_result)))
    except:
        return -1
    WebDriverWait(driver,2)

    value_field = driver.find_element(By.XPATH, xpath_result)

    value_re = re.findall("\d+\.\d+", value_field.text)

    value = float(value_re[0])

    driver.close()

    return value

def get_prize_from_investing(code, instrument):
    xpath = "//*[@id='__next']/div[2]/div[2]/div/div[1]/div/div[1]/div[3]/div/div[1]/div[1]"
    instrument= instrument.upper()
    if instrument == "STOCK":
        url = "https://pl.investing.com/equities/"
    elif(instrument == "ETF"):
        url = "https://pl.investing.com/etfs/"
    else:
        print("wrong instrument")
        return -1

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url + code)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return -1

    prize = driver.find_element(By.XPATH, xpath)
    value_string = str(prize.text)

    if ',' in value_string:
        value_string = value_string.replace(',', '.')

    value = float(value_string)

    return value

def get_prize_from_trading212(code):
    code = code.upper()
    url = "https://www.trading212.com/pl/trading-instruments/invest/"
    xpath = "//*[@id='__next']/main/section[1]/div/div/div[1]/div[1]/section/div[2]/div/label/label[2]"

    chrome_options = Options()
    # trading212 is not working with --headless argument
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url + code)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return -1

    prize = driver.find_element(By.XPATH, xpath)
    value_string = str(prize.text)

    if ',' in value_string:
        value_string = value_string.replace(',', '.')

    value = float(value_string)

    return value

if len(sys.argv) > 1:
    currency_code_list = ["PLN"]
    currency_value_list = [1]
    found = False

    try:
        file = open(sys.argv[1], "r")
    except:
        print("Failed to open file " + sys.argv[1])

    lines = file.readlines()

    for line in lines:
        data = line.split()
        if len(data) != 5:
            print("Error during reading data file")
            continue

        site = data[0]
        count = float(data[1])
        instrument = data[2]
        code = data[3]
        currency_code = data[4].upper()

        error = 0

        for index in range(0, len(currency_code_list)):
            if currency_code == currency_code_list[index]:
                found = True
                break

        if found == True:
            currency_value = currency_value_list[index]
            found = False
        else:
            currency_value = get_exchange_rate_from_xe(currency_code)
            if currency_value == -1:
                error = 1
            else:
                currency_code_list.append(currency_code)
                currency_value_list.append(currency_value)

        instrument_prize = -1
        if site == "investing":
            instrument_prize = get_prize_from_investing(code, instrument)
        elif site == "trading212":
            instrument_prize = get_prize_from_trading212(code)
        else:
            print("Not supported site")
            error = 1

        if instrument_prize == -1:
            error = 1

        if error != 0:
            print("Cannot get price for instrument " + str(code))
        else:
            value = float(count) * float(currency_value) * float(instrument_prize)
            print(code + " (" + instrument + "): " + str(round(value, 2)) + " PLN")
else:
    print("Please provide filename")
    print("The file should consist lines with below data:")
    print("<site> <number> <intrument type> <intrument code> <currency>")
    print("Supported sites: tradinig212.com, investing.pl")
    print("Intrument code should match the one used in site url")