from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import sys

def get_exchange_rate_from_xe(currency, debug):
    url = "https://www.xe.com"
    css_selector_result = "#__next > div:nth-child(4) > div.fluid-container__BaseFluidContainer-sc-qoidzu-0.UiqMO > section > div:nth-child(2) > div > main > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > p.result__BigRate-sc-1bsijpp-1.dPdXSB"
    css_selector_div_from = "#midmarketFromCurrency"
    css_selector_input_from = "#midmarketFromCurrency > div:nth-child(2) > div > input"
    css_selector_div_to = "#midmarketToCurrency"
    css_selector_input_to = "#midmarketToCurrency > div:nth-child(2) > div > input"
    css_selector_button_convert = "#__next > div:nth-child(4) > div.fluid-container__BaseFluidContainer-sc-qoidzu-0.UiqMO > section > div:nth-child(2) > div > main > div > div.currency-converter__SubmitZone-sc-zieln1-2.hQloAE > button"

    currency = currency.upper()

    chrome_options = Options()
    if debug == False:
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url)

    try:
        select_from = driver.find_element(By.CSS_SELECTOR, css_selector_div_from)
        select_from.click()
    except:
        print("Cannot find div from")
        return -1

    try:
        select_input_from = driver.find_element(By.CSS_SELECTOR, css_selector_input_from)
        WebDriverWait(driver, 2)
        select_input_from.send_keys(currency)
        WebDriverWait(driver, 2)
        select_input_from.send_keys(Keys.ENTER)
        WebDriverWait(driver, 5)
    except:
        print("Cannot set curency from")
        return -1
    
    try:
        select_to = driver.find_element(By.CSS_SELECTOR, css_selector_div_to)
        select_to.click()
    except:
        print("Cannot find div to")
        return -1

    try:
        select_input_to = driver.find_element(By.CSS_SELECTOR, css_selector_input_to)
        WebDriverWait(driver, 2)
        select_input_to.send_keys("PLN")
        WebDriverWait(driver, 2)
        select_input_to.send_keys(Keys.ENTER)
        WebDriverWait(driver, 5)
    except:
        print("Cannot set currency to")
        return -1

    try:
        button = driver.find_element(By.CSS_SELECTOR, css_selector_button_convert)
        button.click()
    except:
        print("Cannot find convert button")
        return -1

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_result)))
    except:
        print("Exchange value not load")
        return -1
    WebDriverWait(driver,2)

    try:
        value_field = driver.find_element(By.CSS_SELECTOR, css_selector_result)
    except:
        print("Cannot find exchange value")
        return -1

    value_re = re.findall("\d+\.\d+", value_field.text)

    try:
        value = float(value_re[0])
    except:
        print("Cannot convert string value to float")
        return -1

    driver.close()

    return value

def get_prize_from_investing(code, instrument, debug):
    xpath = "/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]"
    instrument= instrument.upper()
    if instrument == "STOCK":
        url = "https://pl.investing.com/equities/"
    elif(instrument == "ETF"):
        url = "https://pl.investing.com/etfs/"
    else:
        print("wrong instrument")
        return -1

    chrome_options = Options()
    if debug == False:
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options = chrome_options)

    driver.get(url + code)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return -1

    prize = driver.find_element(By.XPATH, xpath)
    split_text = prize.text.split('\n')

    value_string = str(split_text[0])

    if ',' in value_string:
        value_string = value_string.replace(',', '.')

    try:
        value = float(value_string)
    except:
        print("Cannot convert string value to float")

    return value

def get_prize_from_trading212(code, debug):
    code = code.upper()
    url = "https://www.trading212.com/pl/trading-instruments/invest/"
    xpath = "//*[@id='__next']/main/section[1]/div/div/div[1]/div[1]/section/div[2]/div/label/label[2]"

    chrome_options = Options()
    if debug == False:
        # trading212 is not working with --headless argument
        #chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument('--log-level=3')
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

    try:
        value = float(value_string)
    except:
        print("Cannot convert string value to float")

    return value

if len(sys.argv) > 1:
    currency_code_list = ["PLN"]
    currency_value_list = [1]
    found = False
    debug = False

    try:
        file = open(sys.argv[1], "r")
    except:
        print("Failed to open file " + sys.argv[1])

    if len(sys.argv) > 2:
        debug = (sys.argv[2] == "debug")

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
            currency_value = get_exchange_rate_from_xe(currency_code, debug)
            if currency_value == -1:
                error = 1
            else:
                currency_code_list.append(currency_code)
                currency_value_list.append(currency_value)

        instrument_prize = -1
        if site == "investing":
            instrument_prize = get_prize_from_investing(code, instrument, debug)
        elif site == "trading212":
            instrument_prize = get_prize_from_trading212(code, debug)
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