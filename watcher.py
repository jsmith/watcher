import http.client
import os
import smtplib
import time
import urllib.request

import difflib

import bs4
import yaml

with open('.watcher.yaml') as f:
    config = yaml.load(f)


def send_email(url):
    msg = 'WATCHER: {}'.format(url)
    # set the 'from' address,
    fromaddr = 'jacobsmithunb@gmail.com'
    # set the 'to' addresses,
    toaddrs = ['jacob.smith@unb.ca']

    # setup the email server,
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # add my account login name and password,
    server.login("meail", "password")

    # Print the email's contents
    print('From: ' + fromaddr)
    print('To: ' + str(toaddrs))
    print('Message: ' + msg)

    # send the email
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


while True:
    for category_name in config:
        category = config[category_name]

        for url_name in category:
            url = category[url_name]

            path = os.path.join(os.path.expanduser('~'), '.watcher', category_name, url_name)
            if not os.path.exists(path):
                previous_contents = None
            else:
                with open(path) as f:
                    previous_contents = f.read()

            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req)
                contents = resp.read()
                contents = contents.decode()
            except http.client.RemoteDisconnected:
                contents = urllib.request.urlopen(url).read()

            if previous_contents is None:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(contents)

                continue

            ignore = ['html', 'head', 'script', 'style', 'body']
            check = ['a', 'p', 'li', 'h1', 'h2', 'h3', 'string', 'em', 'pre', 'code']

            soup = bs4.BeautifulSoup(contents, "html.parser")
            for l1, l2 in zip(previous_contents.split('\n'), contents.split('\n')):
                if l1.strip() != l2.strip():
                    break
            else:
                continue

            with open(path, 'w') as f:
                f.write(contents)
            send_email(url)

    days = 1
    time.sleep(days * 24 * 60 * 60)
