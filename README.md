# Watcher
Periodically check websites for changes & send notification emails!

## Why?
Most sites (except some blogs) don't offer any way for you to receive a notification when their website has been updated. There were a few sites that I needed to stay updated with so I made this simple script.

## Usage
Create a file in your home directory named `.watcher.yaml` (ex. `~/.watcher.yaml`). The file contents should look something like this:
```yaml
email: <youremail>@gmai.com
password: <yourpassword>

# Now the create whatever you want. These are just some examples. Make sure to follow the same format
blogs:
  - http://blog.samaltman.com

internships:
  - facebook: https://www.facebook.com/careers/university/internships/engineering
  - paypal: https://www.paypal.com/ca/webapps/mpp/jobs/students-and-grads/undergraduate-internships-close
```

Then run these commands:
```
sudo apt-get install chromium-chromedriver
pip install -r requirements.txt
python watcher.py
```
