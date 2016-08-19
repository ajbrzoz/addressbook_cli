"""This module contains Person class used for creating and modifying entries in the addressbook"""

import datetime as dt

from addressbook.ab_parsers import *


class Person(object):
    """Class for creating and modifying entries in the addressbook"""

    def __init__(self, name, surname, email, phone, mode='PL'):
        """
        Attributes:
            name (str): Person's name
            surname (str): Person's surname
            email (str): Person's e-mail address
            phone (str): Person's phone number
            mode ('PL'/'US'): Defines the style of presenting the phone number
        """
        self.name = name.lower().title()
        self.surname = surname.lower().title()
        self.email = email_valid(email)

        self.phone, self.phone_area, self.phone_num = phone_parser(phone, mode)

        # Person's id based on combined surname and name. Used for comparison of two objects and for searching.
        self.personid = str(self.surname.title() + "_" + self.name.title())
        # Person's birthday. Optional. Can be set separately.
        self.birthday = None
        # Year of birth. Extracted from the birthday. Used for calculating age.
        self.year = None
        # Month of birth. Extracted from the birthday. Used for sorting purposes.
        self.month = None
        # Day of birth. Extracted from the birthday. Used for sorting purposes.
        self.day = None
        # Person's city. Optional. Can be set separately.
        self.city = None
        # Person's street name. Optional. Can be set separately.
        self.streetname = None
        # Person's street number. Optional. Can be set separately.
        self.streetnumber = None

    def __repr__(self):
        return '<{0}: {1}, {2}, {3}, {4}>'.format(self.__class__.__name__, self.name, self.surname, self.email,
                                                  self.phone)

    def __eq__(self, other):
        if hasattr(other, 'personid'):
            return self.personid.__eq__(other.personid)

    def __ne__(self, other):
        if hasattr(other, 'personid'):
            return self.personid.__ne__(other.personid)

    def __lt__(self, other):
        return self.personid < other.personid

    def __setattr__(self, key, value):
        if isinstance(value, str) and key != 'email':
            value = value.title()

        if key == 'email':
            value = email_valid(value)

        elif key == 'phone':
            a, b, c = phone_parser(value)
            return (super().__setattr__(key, a),
                    super().__setattr__('phone_area', b),
                    super().__setattr__('phone_num', c))

        elif key == 'street':
            # specifying both street name and number is obligatory in this case
            if value.replace(' ', '').isalpha():
                raise WrongInput("You have not chosen a street name.")
            if value.isdecimal():
                raise WrongInput("You have not chosen a street number.")

            a, b = street_parser(value)
            return (super().__setattr__('streetname', a),
                    super().__setattr__('streetnumber', b))

        elif key == 'streetname' and value is not None:
            a, b = street_parser(value, self.streetnumber or ' ')
            return (super().__setattr__(key, a),
                    super().__setattr__('streetnumber', b))

        elif key == 'streetnumber' and value is not None:
            a, b = street_parser(self.streetname or ' ', value)
            return (super().__setattr__(key, b),
                    super().__setattr__('streetname', a))

        elif key == 'birthday' and value is not None:
            y, m, d = date_parser(value)
            try:
                birthday = dt.date(y, m, d)
                return (super().__setattr__(key, birthday),
                        super().__setattr__('year', birthday.year),
                        super().__setattr__('month', birthday.month),
                        super().__setattr__('day', birthday.day))
            except ValueError as ex:
                raise WrongInput(ex.__str__())

        return super().__setattr__(key, value)

    def get_details(self):
        """Get list of attributes' names and values from the Person dictionary"""
        keys = ['surname', 'name', 'email', 'phone', 'birthday', 'city', 'streetname', 'streetnumber']
        names = (k.capitalize() for k in keys)
        vals = (self.__getattribute__(k) for k in keys)
        details = ('{}: {}'.format(a, b) for a, b in zip(names, vals) if b is not None)
        return list(details)

    def get_age(self):
        """Function for calculating age from date of birth
        (works only if the self.birthday is not None)"""

        today = dt.date.today()

        if self.birthday is None:
            raise ValueError("The birthday has not been set.")
        result = today.year - self.birthday.year - (
            (today.month, today.day) < (self.birthday.month, self.birthday.day))
        if result < 0:
            raise ValueError("Judging by the date of birth, this person has not been born yet.")
        return result
