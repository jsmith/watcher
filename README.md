# Watcher
Periodically check websites for changes & send notification emails!

## Why?
Most sites (except some blogs) don't offer any way for you to receive a notification when their website has been updated. There were a few sites that I needed to stay updated with so I made this simple script. To determine if a site has changed, this script counts a number of keywords and compare the count to the previous count.

## Usage
Create a file in your home directory named `.watcher.yaml` (ex. `~/.watcher.yaml`). Alternatively, place it wherever you want and pass the path in as the first argument to the `watcher.py` script. The file contents should look something like this:
```yaml
email: <youremail>@gmail.com  # the email to send the email from
password: <yourpassword>
destination: <destination>@gmail.com  # the email to send the email to


# Now the create whatever you want. These are just some examples. Make sure to follow the same format
sites:
  samaltman:
    url: http://blog.samaltman.com
    keys: [posted]

  facebook:
    url: https://www.facebook.com/careers/university/internships/engineering
    keys: [fall, engineering, software]
```

Make sure to have [pipenv](https://github.com/pypa/pipenv/) installed then run these commands:
```
sudo apt-get install chromium-chromedriver
pipenv install
pipenv run python watcher.py
```
