from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import sys
import time
import prettytable
import json

class Driver:
    def __init__(self, url, debug = False, strategy = "normal"):
        if type(url) != str:
            raise TypeError("Invalid url")

        if type(debug) != bool:
            raise TypeError("Invalid debug flag")

        if type(strategy) != str:
            raise TypeError("Invalid stategy")
        
        if strategy not in {"normal", "eager", "none"}:
            raise ValueError("Invalid strategy value")

        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        chrome_options.page_load_strategy = strategy
        if debug == False:
            #chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_argument('--log-level=3')

        self.__web = webdriver.Chrome(options = chrome_options)
        try:
            self.__web.get(url)
        except:
            raise RuntimeError("Failed to open url")

    def __del__(self):
        if self.__web != None:
            self.__web.close()

    @property
    def web(self):
        if self.__web != None:
            return self.__web
        else:
            raise RuntimeError("No webdriver created")


def get_exchange_rate_from_xe(currency, page_json, debug = False, ):
    if type(currency) != str:
        raise TypeError("Invalid currency")

    currency = currency.upper()

    if type(debug) != bool:
        raise TypeError("Invalid debug flag")

    if type(page_json) != dict:
        raise TypeError("Invalid page json")

    driver = Driver(page_json["url"], debug)

    try:
        select_from = driver.web.find_element(By.CSS_SELECTOR, page_json["css_selector_div_from"])
        select_from.click()
    except:
        raise RuntimeError("Cannot find div from")

    try:
        select_input_from = driver.web.find_element(By.CSS_SELECTOR, page_json["css_selector_input_from"])
        WebDriverWait(driver.web, 2)
        select_input_from.send_keys(currency)
        time.sleep(1)
        select_input_from.send_keys(Keys.ENTER)
    except:
        raise RuntimeError("Cannot set curency from")

    try:
        select_to =  driver.web.find_element(By.CSS_SELECTOR, page_json["css_selector_div_to"])
        select_to.click()
    except:
        raise RuntimeError("Cannot find div to")

    try:
        select_input_to =  driver.web.find_element(By.CSS_SELECTOR, page_json["css_selector_input_to"])
        WebDriverWait(driver.web, 2)
        select_input_to.send_keys("PLN")
        time.sleep(1)
        select_input_to.send_keys(Keys.ENTER)
    except:
        raise RuntimeError("Cannot set currency to")

    try:
        button = driver.web.find_element(By.CSS_SELECTOR, page_json["css_selector_button_convert"])
        button.click()
        time.sleep(2)
    except:
        raise RuntimeError("Cannot find convert button")

    try:
        WebDriverWait(driver.web, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, page_json["css_selector_result"])))
    except:
        raise RuntimeError("Exchange value not load")

    WebDriverWait(driver.web, 2)

    try:
        value_field = driver.web.find_element(By.CSS_SELECTOR, page_json["css_selector_result"])
    except:
        raise RuntimeError("Cannot find exchange value")

    pattern = r"(\d+\.\d+)\s+PLN"
    value_re = re.search(pattern, value_field.text)

    try:
        value = float(value_re.group(1))
    except:
        raise RuntimeError("Cannot convert value")

    return value

def get_prize_from_investing(code, instrument, page_json, debug = False):
    if type(code) != str:
        raise TypeError("Invalid code")

    if type(instrument) != str:
        raise TypeError("Invalid instrument")

    instrument= instrument.upper()

    if instrument not in {"STOCK", "ETF"}:
        raise ValueError("Invalid instrument value")

    if type(debug) != bool:
        raise TypeError("Invalid debug flag")

    if type(page_json) != dict:
        raise TypeError("Invalid page json")

    if instrument == "STOCK":
        url = page_json["url_stock"]
    else:
        url = page_json["url_etf"]

    complete_url = url + code

    driver = Driver(complete_url, debug, 'none')

    time.sleep(2)

    try:
        prize = driver.web.find_element(By.CSS_SELECTOR, page_json["selector"])
        split_text = prize.text.split('\n')
    except:
        raise RuntimeError("Cannot get value for string")

    value_string = str(split_text[0])

    if ',' in value_string:
        value_string = value_string.replace(',', '.')

    try:
        value = float(value_string)
    except:
        raise RuntimeError("Cannot convert string value to float")

    return value

def get_prize_from_trading212(code, page_json, debug = False):
    if type(code) != str:
        raise TypeError("Invalid code")

    if type(debug) != bool:
        raise TypeError("Invalid debug flag")

    if type(page_json) != dict:
        raise TypeError("Invalid page json")

    code = code.upper()

    complete_url = page_json["url"] + code

    driver = Driver(complete_url, debug)

    try:
        WebDriverWait(driver.web, 10).until(EC.presence_of_element_located((By.XPATH, page_json["xpath"])))
    except:
        raise RuntimeError("Prize does not load")

    prize = driver.web.find_element(By.XPATH, page_json["xpath"])
    value_string = str(prize.text)

    if ',' in value_string:
        value_string = value_string.replace(',', '.')

    try:
        value = float(value_string)
    except:
        raise RuntimeError("Cannot convert string value to float")

    return value

if len(sys.argv) > 1:
    currency_code_list = ["PLN"]
    currency_value_list = [1]
    found = False
    debug = False

    with open(sys.argv[1], "r") as input_file:
        try:
            lines = input_file.readlines()
        except:
            print("Failed to open file " + sys.argv[1])

    with open("xe.json") as xe:
        try:
            xe_json = json.load(xe)
        except:
            print("Failed to open xe.json")

    with open("investing.json") as investing:
        try:
            investing_json = json.load(investing)
        except:
            print("Failed to open investing.json")

    with open("trading.json") as trading:
        try:
            trading_json = json.load(trading)
        except:
            print("Failed to open trading.json")

    if len(sys.argv) > 2:
        debug = (sys.argv[2] == "debug")

    table = prettytable.PrettyTable(["Element", "Wartość"])

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
            try:
                currency_value = get_exchange_rate_from_xe(currency_code, xe_json, debug)
            except Exception as e:
                print(e)
                print("Failed to get exchange rate for " + currency_code)
                continue
            else:
                currency_code_list.append(currency_code)
                currency_value_list.append(currency_value)

        instrument_prize = -1
        try:
            if site == "investing":
                instrument_prize = get_prize_from_investing(code, instrument, investing_json, debug)
            elif site == "trading212":
                instrument_prize = get_prize_from_trading212(code, trading_json, debug)
            else:
                print("Not supported site")
                continue
        except Exception as e:
            print(e)
            print("Failed to get prize for " + instrument + " " + code)
        else:
            value = float(count) * float(currency_value) * float(instrument_prize)
            table.add_row([(code + " " + instrument), str(round(value, 2))])

    print(table)
else:
    print("Please provide filename")
    print("The file should consist lines with below data:")
    print("<site> <number> <intrument type> <intrument code> <currency>")
    print("Supported sites: tradinig212.com, investing.pl")
    print("Intrument code should match the one used in site url")