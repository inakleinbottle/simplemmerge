from __future__ import print_function

from collections import namedtuple

Recipient = namedtuple('Recipient', ('address', 'name', 'data'))



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

def send_emails(datafile, template, username, sender=None,
                password=None, host='', port=0):
    '''Connect to the server and send emails.'''
    import os
    from pkg_resources import resource_filename

    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser

    parser = ConfigParser()
    parser.read([resource_filename(__name__, 'server.ini'),
                os.path.join(os.path.expanduser('~'), '.mmerge.ini')])
    if not sender:
        temp = update_from_config(parser, 'user', 'address')
        sender = temp if temp else get_sender()
    if not username:
        temp = update_from_config(parser, 'user', 'username')
        username = temp if temp else get_username(sender)


    if not host:
        host = update_from_config(parser, 'server', 'host')
    if not port:
        port = int(update_from_config(parser, 'server', 'port'))

    template_, template_vars = get_template(template)
    messages = construct_messages(read_csv(datafile),
                                  template_,
                                  template_vars,
                                  sender)

    if not password:
        temp = update_from_config(parser, 'user', 'password')
        password = temp if temp else get_password()
        del temp

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
    import re

    with open(path, 'r') as f:
        template = f.read()

    # remove any comment lines
    template = re.sub(r'^(\s*)#.*$', '', template, flags=re.MULTILINE).strip()

    # Get the template variables
    # The order must be preserved so the fields match the correct input in the
    # data csv file.
    found = re.findall(r'(?<!\\)\$(\w+)', template)
    template_vars = []
    for match in found:
        if not match in template_vars:
            template_vars.append(match)

            # also replace the the strings with the correct format string.
            template = re.sub(r'(?<!\\)\$' + match, '{' + match + '}', template)

    # finally replace any escaped \$ with $
    template = template.replace(r'\$', '$')

    return template, template_vars

def construct_messages(recipts, template, template_vars, sender):
    '''Construct the message text based for each recipient.'''

    # first remove the mandatory variables
    t_vars = template_vars[3:]
    # If there are template variables, we should map to them.
    if template_vars:
        messages = {}
        for recip in recipts:
            if not len(recip.data) == len(t_vars):
                raise RuntimeError('Number of data fields does not match '
                                   'the number of replacement tags.')
            keywords = {'sender' : sender,
                        'address' : recip.address,
                        'name' : recip.name
                        }
            keywords.update(dict(zip(t_vars, recip.data)))
            messages[recip.address] = template.format(**keywords)
    else:
        # otherwise just go by position.
        messages = {recip.address : template.format(sender,
                                                    recip.address,
                                                    recip.name,
                                                    *recip.data)
                    for recip in recipts}
    return messages

def create_template(path):
    '''Create a template from the default.'''
    import pkgutil

    data = pkgutil.get_data(__name__, 'template.txt')
    with open(path, 'w') as f:
        f.write(data.decode())

def create_config():
    '''Create a local template file in the standard location.'''
    import os
    import shutil
    from pkg_resources import resource_filename
    local_config_path = os.path.join(os.path.expanduser('~'),
                                     '.mmerge.ini')
    default_config = resource_filename(__name__, 'server.ini')
    shutil.copy(default_config, local_config_path)
    print(local_config_path)

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description='''\
    Simple mail merge program that reads recipient data from a csv file and
    applies a template before sending the individualised emails to each
    recipient. The data file should be a csv file, with the email address in the
    first position, name of the recipient in the second, and then the message
    data separated by variable. See the README document for additional guidance.
    ''')


    parser.add_argument('-T', '--new-template', default=None,
                        help=('Create a new template at the specified path. The'
                              ' program will exit upon creation.'))
    parser.add_argument('--make-config', action='store_true',
                        help=('Create a local configuration file in the home '
                              'directory. The path of the config file is '
                              'printed upon execution and the program will '
                              'terminate.'))
    parser.add_argument('-u','--username', default=None,
                        help='Username to use when logging on to the server.')
    parser.add_argument('datafile', nargs='?',
                        help=('CSV file containing the addresses, '
                              'names, and data to be sent.'))
    parser.add_argument('template', nargs='?',
                        help=('Template message to be populated with '
                              'user data.'))
    args = parser.parse_args()


    if args.new_template:
        create_template(args.new_template)
    elif args.make_config:
        create_config()
    else:
        send_emails(args.datafile, args.template, args.username)






if __name__ == '__main__':
    main()
