import logging
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bs4
import yaml
from selenium import webdriver

with open(os.path.join(os.path.expanduser('~'), '.watcher.yaml')) as f:
    config = yaml.load(f)

email = config['email']
password = config['password']

del config['email']
del config['password']


IGNORE = ['[document]', 'html', 'head', 'script', 'style', 'body', 'meta', 'title', 'style', 'div', 'noscript']

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def same(new_soup, old_soup):
    new_children = new_soup.findChildren()
    old_children = old_soup.findChildren()

    # We can't just compare lengths the zip the children together. Sometimes pages will have different lengths but the same content.
    new = 0
    old = 0
    while True:
        if new >= len(new_children) or old >= len(old_children):
            break

        new_element = new_children[new]
        old_element = old_children[old]

        new += 1
        old += 1

        if new_element.name != old_element.name:
            if len(new_children) > len(old_children):
                new += 1
                continue
            elif len(old_children) > len(new_children):
                old += 1
                continue

            logger.info('New element name ({}) does not match old element name ({})!'.format(new_element.name, old_element.name))
            return False

        if new_element.name in IGNORE:
            continue

        if new_element.text.strip() != old_element.text.strip():
            logger.info('Found mismatch element:\n{}\nvs.{}'.format(old, new_element.text, old_element.text))
            return False

    return True


def send_email(url):
    destination = ['jacob.smith@unb.ca']

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = destination[0]
    msg['Subject'] = "Watcher: {}".format(url)

    body = "Changes in {}".format(url)
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(email, password)
    server.sendmail(email, destination, msg.as_string())
    server.quit()


def main():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', chrome_options=options)
    while True:
        for category_name in config:
            category = config[category_name]

            for url_name in category:
                url = category[url_name]
                logger.info('Checking {}'.format(url))

                path = os.path.join(os.path.expanduser('~'), '.watcher', category_name, url_name)
                if not os.path.exists(path):
                    previous_contents = None
                else:
                    with open(path) as f:
                        previous_contents = f.read()

                driver.get(url)
                contents = driver.page_source

                if previous_contents is None:
                    logger.info('Previous contents of {} is None. Writing contents to {}!'.format(url, path))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w') as f:
                        f.write(contents)

                    continue

                old_soup = bs4.BeautifulSoup(previous_contents, "html.parser")
                new_soup = bs4.BeautifulSoup(contents, "html.parser")
                if same(new_soup, old_soup):
                    continue

                with open(path, 'w') as f:
                    logger.info('Overwriting contents of {}'.format(path))
                    f.write(contents)

                send_email(url)

        logger.info('Sleeping :)')
        days = 1
        time.sleep(days * 24 * 60 * 60)


if __name__ == '__main__':
    main()

