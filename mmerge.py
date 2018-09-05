#!/usr/bin/python

import os.path as osp
from collections import namedtuple

Recipient = namedtuple('Recipient', ('address', 'name', 'data'))

CONFIG = osp.join(osp.dirname(osp.abspath(__file__)), 'server.ini')

def read_csv(path):
    '''Read the csv file of indented recipients.'''
    import csv

    with open(path, 'r') as f:
        reader = csv.reader(f)
        

    
        lst = [Recipient(row[0].strip(), row[1].strip(), row[2:])
               for row in reader]
        
    return lst

def get_user():
    '''Get the sender details.'''
    import getpass
    address = input('Email address: ')
    username = input('Username: ')
    password = getpass.getpass()
    return address, username, password

def get_password():
    '''Get the passwod if it has not been provided.'''
    from getpass import getpass
    return getpass()

def get_username(sender):
    '''Get the username to log into the server.'''
    user = input('Username [sender addr]: ')
    return user if user else sender

def get_sender():
    '''Get the sender email address.'''
    return input('Email address: ')

def update_from_config(parser, section, name):
    '''Check the config file for settings.'''
    try:
        return parser.get(section, name)
    except Exception:
        return ''

def send_emails(datafile, template, username, sender=None, password=None, host='', port=0):
    '''Connect to the server and send emails.'''
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser

    parser = ConfigParser()
    parser.read(CONFIG)
    if not sender:
        temp = update_from_config(parser, 'user', 'address')
        sender = temp if temp else get_sender()
    if not username:
        temp = update_from_config(parser, 'user', 'username')
        username = temp if temp else get_username(sender)
    if not password:
        temp = update_from_config(parser, 'user', 'password')
        password = temp if temp else get_password()
        del temp

    if not host:
        host = update_from_config(parser, 'server', 'host')
    if not port:
        port = int(update_from_config(parser, 'server', 'port'))

    messages = construct_messages(read_csv(datafile),
                                  get_template(template),
                                  sender)
    
    
    if port == 587:
        from smtplib import SMTP as SMTP
        smpt = SMTP(host, port)
        smtp.starttls()
    else:
        from smtplib import SMTP_SSL as SMTP
        smtp = SMTP(host, port)

    
    try:        
        smtp.login(username, password)

        for addr, msg in messages.items():
            smtp.sendmail(sender, addr, msg)
    finally:
        smtp.quit()


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

    parser.add_argument('-u','--username',
                        help='Username to use when logging on to the server.')

    parser.add_argument('datafile',
                        help=('CSV file containing the addresses, '
                              'names, and data to be sent.'))
    parser.add_argument('template',
                        help=('Template message to be populated with '
                              'user data.'))
    args = parser.parse_args()

    
    send_emails(args.datafile, args.template, args.username)
    

    



if __name__ == '__main__':
    main()
