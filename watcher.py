import logging
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml
from selenium import webdriver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime) %(levelname)-5.5s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def send_email(url, email, password):
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
        file = os.path.join(os.path.expanduser('~'), '.watcher.yaml')
        with open(file) as f:
            config = yaml.load(f)

        email = config['email']
        password = config['password']
        sites = config['sites']

        for name in sites:
            information = sites[name]
            if 'counts' not in information:
                information['counts'] = {}

            url = information['url']
            keys = information['keys']
            previous_counts = information['counts']

            logger.info('Checking {}'.format(url))

            driver.get(url)
            contents = driver.page_source

            diffs = {}
            for key in keys:
                previous_count = previous_counts.get(key)
                count = contents.count(key)

                if previous_count is None:
                    logger.info('Previous count of {} is None. Writing {} as previous count.'.format(key, count))
                    previous_counts[key] = count
                    continue

                if previous_count != count:
                    diffs[key] = abs(previous_count - count)

            if diffs:
                send_email(url, email, password)

        with open(os.path.join(os.path.expanduser('~'), '.watcher.yaml'), 'w') as f:
            yaml.dump(config, f)

        logger.info('Sleeping :)')
        days = 1
        time.sleep(days * 24 * 60 * 60)


if __name__ == '__main__':
    main()
