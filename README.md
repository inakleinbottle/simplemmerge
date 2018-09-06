# simplemmerge
A simple mail merge program that applies a standard template to the rows in a csv file and then sends individual emails to each recipient.

## Basic usage
From the terminal (or PowerShell/Command Prompt on Windows) run mmerge --help to bring up the command line help information. For simple use, use
```
mmerge <path_to_data> <path_to_template>
```
where the `path_to_data` should be a valid path that points to a csv file containing the necessary data. The format of the csv file should be as follows:
```
<address>,<name>,<field1>,<field2>,...,<fieldn>
```
where the `fieldi` represent the replacement fields different from the sender, address, and name of the recipient. The `path_to_template` should be a valid path pointing to a simple text file that contains the full email template, including email headers. A basic template is provided with the package, and can be copied to a specified directory using
```
mmerge -T <path>
```
where path is the desired destination. The contents of this standard template are as follows:
```
# Simple mail merge template
# The lines starting with # will be automatically removed.
# To add a replacement text marker, use $name where name
# is the name of the field that should replace $name in
# the final email. Name tags can be used more than once,
# but the order in which the first instance of each tag
# appears should match the corresponding 'column' in the
# data file provided.

#The sample template follows.

To: $address
From: $sender
Bcc: $sender
Subject: Test email

Hello $name,

This a test of a simple mail merge. You may wish to consult the README document, which can be found on the GitHub page: $github.

Regards,

Me
```
An example row for the data file that could be used with the above template is
```
user@example.com,User,https://github.com/inakleinbottle/simplemmerge
```
Note that you do not need to provide the `$sender` information since it will be automatically added during formatting. Each tag can be used more than once in the message, but the tags must match their meaning in the data file. In this example, $github would be the first (and only) additional field after `<name>` in the data file.


## Installation
The program can be installed using the Python installation tool pip. Use
```
python -m pip install git+https://github.com/inakleinbottle/simplemmerge.git
```
to install the program for all users, or add the `--user` tag after `install` to only install for you.

Alternatively, you can download a ZIP file containing the current code from https://github.com/inakleinbottle/simplemmerge by clicking on the on 'clone or download' button. Once downloaded, extract to the desired directory and run
```
python setup.py
```
from a console (in the directory).

Installing the program using pip will also install the command line program `mmerge` that can be used from the console/PowerShell/Command Prompt.

## Configuration
A default configuration file is included in the distribution, but you should update this configuration file using
```
mmerge --make-config
```
which will make a new configuration file in the home directory (~/.mmerge.ini on Unix); the path will be printed as output. Your email address and server username can be added to this file, or they can be omitted and you will be prompted on executing the command.
