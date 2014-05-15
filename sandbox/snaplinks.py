import os
from datetime import date
from pprint import pprint
from askmanta.environment import client

root = '/stdbrouw/stor/newslynx-sandbox'

pprint(client.ls('/stdbrouw/stor'))

client.mkdir(root)
test = os.path.join(root, 'latest.txt')
bkup = os.path.join(root, date.today().isoformat() + '.txt')
client.put_object(test, 'This is a test file.')
client.ln(test, bkup)
print 'test', client.get_object(test)
client.delete_object(test)
print 'bkup', client.get_object(bkup)