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
        if self.__web is not None:
            self.__web.close()

    @property
    def web(self):
        if self.__web is not None:
            return self.__web
        else:
            raise RuntimeError("No webdriver created")


def get_exchange_rate_from_xe(currency, debug):
    url = "https://www.xe.com"
    css_selector_result = "#__next > main > div:nth-child(5) > div > section.relative.w-full.bg-gradient-to-l.from-blue-850.to-blue-700.bg-no-repeat > div.relative.m-auto.box-content.max-w-\[1024px\].px-4.py-8.md\:px-10.md\:pt-16.lg\:pt-20 > div > div > div > div:nth-child(1) > p.text-lg.font-semibold.text-xe-neutral-900.md\:text-2xl > span"
    css_selector_div_from = "#midmarketFromCurrency"
    css_selector_input_from = "#midmarketFromCurrency > div:nth-child(2) > div > input"
    css_selector_div_to = "#midmarketToCurrency"
    css_selector_input_to = "#midmarketToCurrency > div:nth-child(2) > div > input"
    css_selector_button_convert = "#__next > main > div:nth-child(5) > section.relative.flex.justify-center.bg-gray-100.pt-8.pb-8.md\:pt-16.md\:pb-16 > div > div > div.flex.flex-col.items-center.gap-6.md\:flex-row.justify-end > button"
    currency = currency.upper()

    driver = Driver(url, debug)

    try:
        select_from = driver.web.find_element(By.CSS_SELECTOR, css_selector_div_from)
        select_from.click()
    except:
        print("Cannot find div from")
        return -1

    try:
        select_input_from = driver.web.find_element(By.CSS_SELECTOR, css_selector_input_from)
        WebDriverWait(driver.web, 2)
        select_input_from.send_keys(currency)
        time.sleep(1)
        select_input_from.send_keys(Keys.ENTER)
    except:
        print("Cannot set curency from")
        return -1
    
    try:
        select_to =  driver.web.find_element(By.CSS_SELECTOR, css_selector_div_to)
        select_to.click()
    except:
        print("Cannot find div to")
        return -1

    try:
        select_input_to =  driver.web.find_element(By.CSS_SELECTOR, css_selector_input_to)
        WebDriverWait(driver.web, 2)
        select_input_to.send_keys("PLN")
        time.sleep(1)
        select_input_to.send_keys(Keys.ENTER)
    except:
        print("Cannot set currency to")
        return -1

    try:
        button = driver.web.find_element(By.CSS_SELECTOR, css_selector_button_convert)
        button.click()
        time.sleep(2)
    except:
        print("Cannot find convert button")
        return -1

    try:
        WebDriverWait(driver.web, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_result)))
    except:
        print("Exchange value not load")
        return -1

    WebDriverWait(driver.web, 2)

    try:
        value_field = driver.web.find_element(By.CSS_SELECTOR, css_selector_result)
    except:
        print("Cannot find exchange value")
        return -1

    pattern = r"(\d+\.\d+)\s+PLN"
    value_re = re.search(pattern, value_field.text)

    try:
        value = float(value_re.group(1))
    except:
        return -1

    return value

def get_prize_from_investing(code, instrument, debug):
    selector = "#__next > div.md\:relative.md\:bg-white > div.relative.flex > div.grid.flex-1.grid-cols-1.px-4.pt-5.font-sans-v2.text-\[\#232526\].antialiased.transition-all.xl\:container.sm\:px-6.md\:gap-6.md\:px-7.md\:pt-10.md2\:gap-8.md2\:px-8.xl\:mx-auto.xl\:gap-10.xl\:px-10.md\:grid-cols-\[1fr_72px\].md2\:grid-cols-\[1fr_420px\] > div.min-w-0 > div.flex.flex-col.gap-6.md\:gap-0 > div.flex.gap-6 > div.flex-1 > div.mb-3.flex.flex-wrap.items-center.gap-x-4.gap-y-2.md\:mb-0\.5.md\:gap-6 > div.text-5xl\/9.font-bold.text-\[\#232526\].md\:text-\[42px\].md\:leading-\[60px\]"
    instrument= instrument.upper()
    if instrument == "STOCK":
        url = "https://pl.investing.com/equities/"
    elif(instrument == "ETF"):
        url = "https://pl.investing.com/etfs/"
    else:
        print("wrong instrument")
        return -1

    complete_url = url + code

    driver = Driver(complete_url, debug, 'none')

    time.sleep(2)

    try:
        prize = driver.web.find_element(By.CSS_SELECTOR, selector)
        split_text = prize.text.split('\n')
    except:
        print("Cannot get value for string")
        return -1

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

    complete_url = url + code

    driver = Driver(complete_url, debug)

    try:
        WebDriverWait(driver.web, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return -1

    prize = driver.web.find_element(By.XPATH, xpath)
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
            currency_value = get_exchange_rate_from_xe(currency_code, debug)
            if currency_value == -1:
                print("Failed to get exchange rate for " + currency_code)
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
            print("Failed to get instrument prize for " + instrument + " " + code)
            error = 1

        if error == 0:
            value = float(count) * float(currency_value) * float(instrument_prize)
            table.add_row([(code + " " + instrument), str(round(value, 2))])

    print(table)
else:
    print("Please provide filename")
    print("The file should consist lines with below data:")
    print("<site> <number> <intrument type> <intrument code> <currency>")
    print("Supported sites: tradinig212.com, investing.pl")
    print("Intrument code should match the one used in site url")