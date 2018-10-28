import logging
import os
import sys
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


def send_email(url, diffs, email, password, destination):
    destination = [destination]

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = destination[0]
    msg['Subject'] = "Watcher: {}".format(url)

    def format_diff(key):
        return f'{key} changed by {diffs[key]}'

    body = f"Changes in {url}\n" + '\n'.join(map(format_diff, diffs))
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(email, password)
    server.sendmail(email, destination, msg.as_string())
    server.quit()


def main(path, times=None):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver_src = '/usr/lib/chromium-browser/chromedriver'
    if not os.path.isfile(driver_src):
        raise FileNotFoundError(f'Make sure to install `chromedriver`. {driver_src} does not exist!')

    driver = webdriver.Chrome(executable_path=driver_src, chrome_options=options)

    check_count = 0
    while True:
        with open(path) as f:
            config = yaml.load(f)

        if 'email' not in config or 'password' not in config:
            raise ValueError('`email` and `password` must be present in the yaml file!')

        if 'sites' not in config:
            raise ValueError('`sites` field must be present in the yaml file!')

        if 'destination' not in config:
            raise ValueError('`destination` field must be present in the yaml file!')           

        email = config['email']
        password = config['password']
        destination = config['destination']
        sites = config['sites']

        if not isinstance(sites, dict):
            raise ValueError('`sites` must be a dictionary')

        for name in sites:
            information = sites[name]

            if not isinstance(information, dict):
                raise ValueError(f'`{name}` must be a dictionary')

            if not isinstance(information, dict):
                raise ValueError(f'`{name}` must be a dictionary')

            if 'url' not in information:
                raise ValueError(f'`{name}` must contain a `url` field')

            if 'keys' not in information:
                raise ValueError(f'`{name}` must contain a `keys` field. We determine if a site has changed by conting the `keys`.')

            if 'counts' not in information:
                logger.info(f'Intilializing counts for {name}')
                information['counts'] = {}

            url = information['url']
            keys = information['keys']
            previous_counts = information['counts']

            if not isinstance(url, str):
                raise ValueError('`url` must be a string')

            if not isinstance(keys, list) or not all([isinstance(key, str) for key in keys]):
                raise ValueError('`keys` must be a list of strings!')

            logger.info(f'===== Checking {url} ======')

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
                logger.info(f'Found change: {diffs}')
                send_email(url, diffs, email, password, destination)

            print()

        with open(path, 'w') as f:
            yaml.dump(config, f)
        
        check_count += 1
        if times is not None and times == check_count:
            break

        logger.info('Sleeping :)')
        days = 1
        time.sleep(days * 24 * 60 * 60)


if __name__ == '__main__':
    path = os.path.join(os.path.expanduser('~'), '.watcher.yaml')
    if len(sys.argv) > 1:
        path = sys.argv[1]
    
    if not os.path.isfile(path):
        raise FileNotFoundError('{} does not exist'.format(path))

    main(path)
