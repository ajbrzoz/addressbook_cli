"""This module contains parsers used by AdressBook"""

import re
from string import digits

from addressbook.ab_exceptions import *


def phone_parser(phone, mode='PL'):
    """Parse strings containing phone number"""

    if not phone:
        raise WrongInput("Input cannot be blank")
    if not isinstance(phone, str):
        raise WrongInput("Invalid phone format")

    if mode == 'PL':
        gsm_prefixes = ['50', '51', '53', '57', '60', '66', '69', '72', '73', '78', '79', '88']
        if phone[:2] in gsm_prefixes:
            phone_pattern = re.compile(r'''
                            # don't match beginning of string
            (\d{0,2})       # area code of 2 digits (e.g. '42')
            \D*             # optional separator
            (\d{3}\D*\d{3}\D*\d{3})   # rest of number - divide into 3 3-digit sequences with optional separators
                                      # (e.g. '605-789-567')
            $               # end of string
            ''', re.VERBOSE)
        else:
            phone_pattern = re.compile(r'''
                            # don't match beginning of string
            (\d{0,2})       # area code of 2 digits (e.g. '42')
            \D*             # optional separator
            (\d{3}\D*\d{2}\D*\d{2})   # rest of number - divide into 3 2-digit sequences with optional separators
                                      # (e.g. '605-78-56')
            $               # end of string
            ''', re.VERBOSE)
    else:
        phone_pattern = re.compile(r'''
                        # don't match the beginning of the string
        (\d{3})         # area code of 3 digits (e.g. '800')
        \D*             # optional separator
        (\d{3}\D*\d{4}\D*\d+)   # rest of number - divide into 3 sequences with optional separators: two obligatory
                                # with 3 and 4 digits, one optional with any number of digits
        $               # end of string
        ''', re.VERBOSE)
    if not re.search(phone_pattern, phone):
        raise WrongInput("Invalid phone format.")

    phone_obj = phone_pattern.search(phone)
    phone_area, phone_num = phone_obj.groups()
    phone = re.sub(r'\D', '', phone_num)
    return phone, phone_area, phone_num


def street_parser(*street_data):
    """Parse tuples and strings containing street name and number

    Attributes:
        *street_data (str/sequence of strings) - Street name and number (in arbitrary order)
    """

    # parsing tuples
    if len(street_data) == 2:
        if not isinstance(street_data[0], str) and not isinstance(street_data[1], str):
            raise WrongInput("Invalid format")
        # street name as the tuple's first item
        strname, strnumber = street_data
        # street number as the tuple's first item
        if street_data[0][0] in digits:
            strname, strnumber = strnumber, strname

    # parsing strings
    else:
        if not isinstance(street_data[0], str):
            raise WrongInput("Invalid format")
        if not street_data[0]:
            raise WrongInput("Input cannot be blank")

        # string starting with street number
        if street_data[0][0] in digits:
            street_pattern = re.compile(r'''
            ^       # beginning of string
            (\d+)   # street number is any number of digits
            \W+     # separator
            (\w+\W*\w*\W*) # street name is one or more words with optional separators
            $       # end of string
            ''', re.VERBOSE)
            street_obj = street_pattern.search(street_data[0])
            strnumber, strname = street_obj.groups()

        # string starting with street name
        else:
            street_pattern = re.compile(r'''
            ^       # beginning of string
            (\w+\W*\w*\s*) # street name is one or more words with optional separators
            \W+     # separator
            (\d+)   # street number is any number of digits
            $       # end of string
            ''', re.VERBOSE)
            street_obj = street_pattern.search(street_data[0])
            (strname, strnumber) = street_obj.groups()

    # replace specific words in street name with their abbreviates
    strname = strname.lower()
    special = {r'\baleje\b': 'Al.', r'\bavenue\b': 'Av.', r'\broad\b': 'Rd.', r'\bsquare\b': 'Sq.',
               r'\bstreet\b': 'St.', r'\bdrive\b': 'Dr.'}
    for key in special:
        strname = re.sub(key, special[key], strname)
    return strname.title(), strnumber


def date_parser(dt_string):
    """Parse strings containing dates

    Attributes:
        *dt_string (str) - Street name and number (in arbitrary order)
    """

    if not dt_string:
        raise WrongInput("Input cannot be blank")
    if not isinstance(dt_string, str):
        raise WrongInput("Invalid date format")

    dt_string = re.sub(r'\b0', '', dt_string)
    date_pattern = re.compile(r'''
    \s*                         # optional whitespace
    ([1-9]|[1,2][0-9]|3[0,1])   # day (1-31)
    [-/.]                        # separator
    ([1-9]|1[0-2])              # month (1-12)
    [-/.]                        # separator
    (\d{4})                     # year (YYYY)
    \s*                         # optional whitespace
    ''', re.VERBOSE)
    if not re.search(date_pattern, dt_string):
        raise WrongInput("Invalid date format.")
    date_obj = date_pattern.search(dt_string)
    day, month, year = date_obj.groups()
    return int(year), int(month), int(day)


def email_valid(email_string):
    """Check if string contain valid email address. It's not actually a parser but serves a similar purpose
    when it comes to input validation)"""
    if not email_string:
        raise WrongInput("Input cannot be blank")
    if not isinstance(email_string, str):
        raise WrongInput("Invalid email address")

    if '@' not in email_string or '.' not in email_string:
        raise WrongInput('Invalid email address. Example of a valid address: johndoe@example.com.')
    else:
        return email_string
