from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)


@app.route('/everytime/<path:url>', methods=['GET'])
def crawl(url):
    url = unquote(url)

    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    try:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#container"))
            )
        except:
            driver.quit()
            return jsonify({'error': 'The page did not load properly or the container element is missing.'}), 404

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')

        container = soup.select("#container")
        if not container:
            return jsonify({'error': 'url 형식을 인식할 수 없습니다. container 오류'}), 404
        container = container[0]

        height = int(container.get('style')[8:-3])
        if not height:
            return jsonify({'error': 'url 형식을 인식할 수 없습니다. '}), 404

        days = soup.select('#container > .wrap > .tablebody td')
        print(len(days))

        data = [{"height": height}]
        count = 0

        for day in days:
            event = []
            events = day.select('div div')
            for i in events:
                title_ = i.select_one('h3')
                if not title_:
                    continue
                title = title_.text

                style = i.get('style') if i.get('style') else None
                if style:
                    styleList = style.split(";")
                    if len(styleList) == 3:
                        top = int(styleList[1][6:-2])
                        height = int(styleList[0][8:-2])
                    else:
                        continue
                else:
                    continue
                event.append({
                    "day": count,
                    "title": title,
                    "top": top,
                    "height": height
                })
            count += 1
            data.append(event)

        return jsonify(data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


