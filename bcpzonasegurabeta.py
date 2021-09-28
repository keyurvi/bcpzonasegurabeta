#! /usr/bin/python3
import base64
import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from multiprocessing import Process
from re import sub
from anticaptchaofficial.imagecaptcha import *
from time import time, sleep

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from cairosvg import svg2png
from flask import Flask, request
from lxml import html
from requests import post
from selenium import webdriver
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def mainworker():
    if request.method == 'GET':
        return "Spider is working OK."
    elif request.method == 'POST':
        utc_now = lambda: datetime.utcnow()
        utc_now = sub(":|\.| ", "_", str(utc_now()))
        spidername = "bcpzonasegurabeta"
        filename = f"{spidername}_{utc_now}.json"
        p = Process(target=saveJSON, args=(filename,))
        p.daemon = True
        p.start()
        return filename


def normalize_whitespace(string):
    string = re.sub(r'(\s)\1{1,}', r'\1', string)
    return re.sub('__+', '_', string)


def slove_image_fun(image):
    captcha_text = get_image_text(image)
    print(captcha_text)
    return captcha_text


def replace_normalize(name):
    return normalize_whitespace(
        str(name).replace('\r', ' ').replace('\n', ' ').replace('\t', ' ').replace('__', '_').strip('_').strip())


def get_image_text(image_res):
    if image_res:
        try:
            try:
                image_res = image_res.split('data:image/png;base64,')[1]
                imgdata = base64.b64decode(image_res)

                f = open('captcha.jpg', 'wb')
                f.write(imgdata)
                f.close()

            except:
                # image_res = image_res.split('data:image/svg+xml;base64,')[1]
                imgdata = base64.b64decode(image_res)
                f = open('captcha.svg', 'wb')
                f.write(imgdata)
                f.close()
                f = open('captcha.svg', 'r')
                svg_code = f.read()
                f.close()
                svg2png(bytestring=svg_code, write_to='captcha.jpg')

            solver = imagecaptcha()
            solver.set_verbose(1)
            solver.set_key("a7cb5e51066442c028b79d4282600bc3")

            captcha_text = solver.solve_and_return_solution("captcha.jpg")

            if captcha_text != 0:
                print("captcha text " + captcha_text)
            else:
                print("task finished with error " + solver.error_code)
            return captcha_text
        except Exception as e:
            print(e)
            pass
        return False


def saveJSON(filename):
    bsc = BlobServiceClient(account_url="https://matikafilestorage.blob.core.windows.net/",
                            credential="ZHefXyWtrOJyAN2mNYKVxC0vYocITMdAUhOeW5JQzTCz/KqtDHgz4hsUpiVm6ViGFkBvuj3WkncABrnYFCFGnw==")
    blob_client = bsc.get_blob_client("spiderjobs", filename)

    password = str(request.headers.get("clave"))
    user_code = str(request.headers.get("rutusuario1"))
    startdate = str(request.headers.get("startdate"))
    start_date = datetime.strptime(startdate, "%d-%m-%Y")
    enddate = str(request.headers.get("enddate"))
    end_date = datetime.strptime(enddate, "%d-%m-%Y")

    request_data = {k.lower(): v for k, v in request.headers.items()}

    # company_code = '01129799'
    # user_code = 'ADMIN001'
    # password = 'MATI0621'
    # start_date = '01/01'+datetime.now().strftime('/%Y')
    # end_date = datetime.now().strftime('%d/%m/%Y')

    # try:
    #     os.remove('/home/ubuntu/spiders/bcpzonasegurabeta/captcha.svg')
    # except:
    #     pass
    # try:
    #     os.remove('/home/ubuntu/spiders/bcpzonasegurabeta/captcha.jpg')
    # except:
    #     pass

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    # driver = webdriver.Chrome(executable_path='/home/chintan/PycharmProjects/advocate/Wallmart/chromedriver', chrome_options=chrome_options)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get('https://bcpzonasegurabeta.viabcp.com/#/iniciar-sesion')
    sleep(5)
    timestart = time()
    try:
        driver.find_element_by_xpath('//*[@name="cardNumber"]').send_keys(user_code)
        sleep(1)

        driver.find_element_by_xpath('//*[@class="icon bcp-lock-o mark-lock-icon"]').click()

        captcha_url = driver.find_element_by_xpath('//*[@class="captcha-border ng-star-inserted"]').get_attribute(
            'src')
        print(captcha_url)
        captcha_text = get_image_text(captcha_url)
        print(captcha_text)

        driver.find_element_by_xpath('//*[@placeholder="Escribe los caracteres"]').send_keys(captcha_text)

        all_images = driver.find_elements_by_xpath('//*[@class="seed-enabled ng-star-inserted"]')

        main_image_dict = {}

        # jobs = []
        next_img = True
        for img in all_images:
            if next_img == False:
                break
            number_image_main = img.get_attribute('src')
            print(number_image_main)
            number_image = number_image_main.split('data:image/svg+xml;base64,')[1]
            data = slove_image_fun(number_image)
            main_image_dict[data] = number_image_main
            next_img = False
            for k in password:
                if k not in main_image_dict.keys():
                    next_img = True

        print(main_image_dict)

        for i in password:
            driver.find_element_by_xpath('(//*[@src="' + main_image_dict[i] + '"])[1]').click()

        driver.find_element_by_xpath('//*[@type="submit"]').click()

        sleep(15)

        try:
            driver.find_element_by_xpath(
                '//*[@class="btn btn-primary btn-md btn-primary mt-20 btn-close-sessions"]').click()
            sleep(15)
        except Exception as e:
            print(str(e))

        try:
            driver.find_element_by_xpath(
                '//*[@class="col-6 col-md-3 btn btn-primary welcome-modal-products-button ng-star-inserted"]').click()
        except Exception as e:
            print(str(e))
        sleep(5)
        try:
            driver.find_element_by_xpath('//*[@class="products-row-m"]').click()
        except Exception as e:
            print(str(e))

        sleep(10)

        response = html.fromstring(driver.page_source)

        all_data = response.xpath('//*[@class="row detail-summary-table-body"]')
        print(all_data)
        all_date = []
        for data in all_data:
            data_dict = {}

            check_date = datetime.strptime(replace_normalize(''.join(data.xpath('.//*[@class="date-td"]/text()'))),
                                           "%d/%m/%Y")
            print(check_date)

            if end_date >= check_date and check_date >= start_date:
                data_dict['fecha'] = replace_normalize(''.join(data.xpath('.//*[@class="date-td"]/text()')))
                data_dict['descripcion'] = replace_normalize(
                    ''.join(data.xpath('.//*[@class="col description-wrapper-td"]/p/text()')))
                print(data_dict['fecha'])
                manto = replace_normalize(''.join(data.xpath('.//*[@class="amount ng-star-inserted"]//text()')))
                print(manto)
                cargo = ''
                abonos = ''
                if '-' in manto and '/ ' in manto:
                    cargo = manto.split('/ ')[-1].strip()
                if '+' in manto and '/ ' in manto:
                    abonos = manto.split('/ ')[-1].strip()
                print(manto)
                print(cargo)
                print(abonos)

                data_dict['cargo'] = cargo.replace(',', '')
                data_dict['abonos'] = abonos.replace(',', '')
                all_date.append(data_dict)

        print(all_date)

        try:
            driver.find_element_by_xpath('//*[@class="dropdown-toggle user-b"]').click()
        except:
            pass
        try:
            driver.find_element_by_xpath('//*[@href="javascript:void(0)"]').click()
        except:
            pass
        try:
            driver.find_element_by_xpath(
                '//*[@class="btn btn-primary col-12 col-md-3 mr-0 mr-md-3 mb-3 mb-md-0 order-md-2 ng-star-inserted"]').click()
        except:
            pass
        finalres = {"status": {"value": 0, "description": "OK", "TimeElapsed": str(int(time() - timestart))},
                    "request": request_data,
                    "items": all_date}
        blob_client.upload_blob(str(finalres), encoding='utf-8',
                                content_settings=ContentSettings(content_type='application/json'))
        # print("There is no data right now.")
        driver.quit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        screen = driver.get_screenshot_as_base64()
        finalres = {"status": {"value": 1, "description": f"Error {exc_type} in line {exc_tb.tb_lineno}",
                               "screenshot": str(screen),
                               "TimeElapsed": str(int(time() - timestart))}, "request": request_data,
                    "items": []}
        blob_client.upload_blob(str(finalres), encoding='utf-8',
                                content_settings=ContentSettings(content_type='application/json'))
        driver.quit()

    # try:
    #     os.remove('/home/ubuntu/spiders/bcpzonasegurabeta/captcha.svg')
    # except:
    #     pass
    # try:
    #     os.remove('/home/ubuntu/spiders/bcpzonasegurabeta/captcha.jpg')
    # except:
    #     pass

    if request.headers.get("EndpointURL") is not None and request.headers.get("EndpointURL") != "":
        lastheaders = {"SpiderJobId": filename}
        post(url=request.headers.get("EndpointURL"), headers=lastheaders)


if __name__ == "__main__":
    handler = RotatingFileHandler('./Logs.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.run()
    #app.run(host='0.0.0.0', port=5000)
