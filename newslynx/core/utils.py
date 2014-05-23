import os
from datetime import date, datetime

import manta

# 
# TODO
# 
# These utilities are also used in the ingestion phase.
# I'm wary of turning `newslynx-core` into one big 
# module with lots of dependencies itself, because 
# I don't really understand the performance impact that 
# would have, but it should be possible to at least 
# create an `utils` folder and add that to `sys.path`.
# 

# Manta expects directory names to end with a trailing slash
def dirname(filename):
    return os.path.dirname(filename) + '/'


def save(filename, data, local=False):
    # askmanta should take care of the abstraction 
    # rather than us, but whatever
    if local:
        filename = os.path.join('data', filename)
        with open(filename, 'w') as f:
            f.write(data)
    else:
        print filename
        client.mkdirp(dirname(filename))
        client.put_object(filename, data)


def versioned_save(directory, extension, data):
    if len(extension) and not extension.startswith('.'):
        extension = '.' + extension

    now = datetime.today().isoformat()[:16]
    latest = os.path.join(directory, 'latest' + extension)
    snaplink = os.path.join(directory, now + extension)
    # Manta is supposed to be strongly consistent, but 
    # it doesn't really look that way...
    save(latest, data)
    client.ln(latest, snaplink)


def silence(fn, retval=None, exceptions=(Exception)):
    def silent_fn(*vargs, **kwargs):
        try:
            return fn(*vargs, **kwargs)
        except exceptions:
            return retval

    return silent_fn


url = os.environ['MANTA_URL']
account = os.environ['MANTA_USER']
key_id = os.environ.get('MANTA_KEY_ID')
signer = None

if key_id:
    signer = manta.SSHAgentSigner(key_id)

root = '/stdbrouw/stor/'
client = manta.MantaClient(url, account, signer)