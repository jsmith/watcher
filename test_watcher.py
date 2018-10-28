import tempfile
import os

import pytest
import yaml

import watcher

def test_watcher():
    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, '.watcher.yml')
        with pytest.raises(FileNotFoundError):
            watcher.main(path)

        config = {
            'email': 'asldfjk@jksldfj.coam',
            'password': 'apsdofjdsaklfj',
            'destination': 'jksa@jacob.scom',
            'sites': {
                'google': {
                    'url': 'https://google.com',
                    'keys': ['google']
                }
            }
        }
        with open(path, 'w') as fp:
            yaml.dump(config, fp)
        
        watcher.main(path, 1)

def test_send_email():
    email = ''
    password = ''
    dst = ''

    watcher.send_email('google.com', {'key': 5}, email, password, dst)
