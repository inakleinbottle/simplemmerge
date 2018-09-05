#/usr/bin/python3

from smtplib import SMTP_SSL as SMTP
from email.message import Message

from collections import namedtuple

Recipient = namedtuple('Recipient', ('address', 'name', 'data'))

def read_csv(path):
    '''Read the csv file of indented recipients.'''
    import csv

    with open(path, 'r') as f:
        lst = [Recipient(address, name, data)
               for address, name, *data in csv.reader(f)]
    return lst

def get_user():
    '''Get the sender details.'''
    import getpass
    address = input('Email address: ')
    username = input('Username: ')
    password = getpass.getpass()
    return address, username, password

def get_server_info():
    from configparser import ConfigParser
    import os.path as osp

    path = osp.join(osp.dirname(osp.abspath(__file__)), 'server.ini')

    parser = ConfigParser()
    parser.read(path)

    host = parser['server']['host']
    port = parser['server']['port']

    return host, port
    


def send_emails(sender, auth, messages, host='', port=0):
    '''Connect to the server and send emails.'''

    with SMTP(host, port) as smtp:
        smtp.login(*auth)

        for addr, msg in messages.items():
            smtp.sendmail(sender, addr, msg)


def get_template(path):
    '''Get the template text from file.'''
    with open(path, 'r') as f:
        template = f.read()

    return template

def construct_messages(recipts, template, sender):
    '''Construct the message text based for each recipient.'''

    return {recip.address : template.format(sender,
                                            recip.address,
                                            recip.name,
                                            *recip.data)
            for recip in recipts}

        

    
    

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('datafile',
                        help=('CSV file containing the addresses, '
                              'names, and data to be sent.'))
    parser.add_argument('template',
                        help=('Template message to be populated with '
                              'user data.'))
    args = parser.parse_args()

    host, port = get_server_info()
    sender, username, password = get_user()

    messages = construct_messages(read_csv(args.datafile),
                                  get_template(args.template),
                                  sender)
    send_emails(sender, (username, password), messages, host=host, port=port)
    

    



if __name__ == '__main__':
    main()
