import copy
import unittest
from random import shuffle
from unittest.mock import patch

from addressbook.main_ab import *


@patch('builtins.input', return_value='y')
def abook_example(mock_input):
    """Create exemplary AddressBook"""

    book = AddressBook()

    names = ['roy'] * 11 + ['pris', 'leon', 'tony', 'zhora', 'ellen', 'annie', 'beatrix', 'rick', 'travis',
                            'tony', 'harry']
    surnames = ['batty'] * 11 + ['stratton', 'kowalski', 'manero', 'stratton', 'ripley', 'hall',
                                 'kiddo', 'blaine', 'bickle', 'montana', 'callahan']
    emails = ['nexus6@gmail.com'] * 11 + ['nero65@walla.com', 'rbatty@gmail.com', 'qwerty123@yandex.ru',
                                          'cthulhu23@gmail.com', 'jkowalski78@onet.pl', 'qwerty123@yandex.ru',
                                          'abcdef@mail.ru', 'johndoe91@yahoo.co.uk', 'ricky@rambler.ru',
                                          'a1@gmail.com', 'foobar@gmail.com']
    phones = ['668678678'] * 11 + ['609876543', '508-123-456', '888.000.000', '33 333 44 55', '425980912',
                                   '(22)7790123', '(12)2156790', '(32) 2222222', '33 333 44 55', '509910820',
                                   '881 000 002']
    cities = ['los angeles'] * 11 + ['springfield', 'hill valley', None, 'metropolis', 'pleasantville',
                                     'stepford', None, 'pleasantville', 'los santos', 'stepford']
    streets = ['baker street 10'] * 11 + ['tverskaya 54', '8 mulholland drive', '189 broad road',
                                          'aleje jerozolimskie 190', 'broadway 287', '100 sunset boulevard',
                                          'sunset boulevard 189', 'elm street 9', '99 arbour road',
                                          'arbat 120', '77 wallaby way']
    birthdays = ['8-1-2016'] * 11 + ['30-11-1968', '18/3/1970', '24.12.2001', '15-12-1991', '3/5/1985',
                                     '9.9.1999', '28-7-1987', '24/12/2001', '9.8.1991']

    for nm, sur, em, ph in zip(names, surnames, emails, phones):
        with suppress_stdout():
            book.__append__(nm, sur, em, ph)

    for contact, c, st, b in zip(book, cities, streets, birthdays):
        to_set = {'city': c, 'street': st, 'birthday': b}
        for key, val in to_set.items():
            setattr(contact, key, val)

    return book


class NewDate(dt.date):
    @classmethod
    def today(cls):
        return cls(2020, 1, 9)


class TestParsers(unittest.TestCase):
    valid_phones = ('668678678', '668-678-678', '668.678.678', '668 678 678', '425109999', '(42)5109999',
                    '(42)5109999', '(42) 5109999', '42 510 99 99', '42 510-99-99')

    street_values = {'baker street 64': ('Baker St.', '64'),
                     '640 madison AVENUE': ('Madison Av.', '640'),
                     'aleje Jerozolimskie 9': ('Al. Jerozolimskie', '9'),
                     '32 Mulholland drive': ('Mulholland Dr.', '32'),
                     '129 broad Road': ('Broad Rd.', '129'),
                     'RED SQUARE 6': ('Red Sq.', '6')}

    def test_email_valid_wrong_input(self):
        """"email_valid should fail at attempt to parse email address that lacks '@' symbol"""
        self.assertRaises(WrongInput, email_valid, 'nexus6gmail.com')

    def test_phone_parser(self):
        """Test if phone numbers are parsed correctly"""

        for num in self.valid_phones:
            if num in self.valid_phones[:4]:
                self.assertEqual(phone_parser(num)[0], '668678678')
            else:
                self.assertEqual(phone_parser(num)[0], '5109999')
                self.assertEqual(phone_parser(num)[1], '42')

    def test_phone_parser_wrong_input(self):
        """phone_parser should fail with invalid phone numbers"""
        invalid = ('66867867', '', 668678678)
        for num in invalid:
            self.assertRaises(WrongInput, phone_parser, num)

    def test_street_parser_street(self):
        """Test if strings with street names and numbers are parsed correctly"""
        for street in self.street_values:
            self.assertEqual(street_parser(street)[0], self.street_values[street][0])
            self.assertEqual(street_parser(street)[1], self.street_values[street][1])

    def test_street_parser_wrong_input(self):
        """__setattr__ should fail with invalid input"""
        invalid = ''
        for inp in invalid:
            self.assertRaises(WrongInput, street_parser, inp)

    def test_date_parser(self):
        """While using __setattr__ with 'birthday' attribute the value should be parsed and four attributes
        ('birthday', 'year', 'month' and 'year') should be set consequently"""
        birthdays = {'01-10-1968': (1968, 10, 1),
                     '1-10-1968': (1968, 10, 1),
                     '31/10/1968': (1968, 10, 31),
                     '31/01/1968': (1968, 1, 31),
                     '31/1/1968': (1968, 1, 31),
                     '31/12/1968': (1968, 12, 31),
                     '24.12.1000': (1000, 12, 24),
                     '24.12.9999': (9999, 12, 24)}
        for date in birthdays:
            self.assertEqual(date_parser(date), (birthdays[date]))


class TestPerson(unittest.TestCase):
    default_vals = ['roy', 'batty', 'nexus6@gmail.com', '668678678']

    valid_phones = ('668678678', '668-678-678', '668.678.678', '668 678 678', '425109999', '(42)5109999',
                    '(42)5109999', '(42) 5109999', '42 510 99 99', '42 510-99-99')

    street_values = {'baker street 64': ('Baker St.', '64'),
                     '640 madison AVENUE': ('Madison Av.', '640'),
                     'aleje Jerozolimskie 9': ('Al. Jerozolimskie', '9'),
                     '32 Mulholland drive': ('Mulholland Dr.', '32'),
                     '129 broad Road': ('Broad Rd.', '129'),
                     'RED SQUARE 6': ('Red Sq.', '6')}

    @staticmethod
    def default_person(vals=default_vals):
        """Create exemplary Person object"""
        return Person(*vals)

    def test_person_constructor(self):
        """Test if all basic attributes are set properly """
        roy_batty = self.default_person()
        self.assertEqual(roy_batty.name, 'Roy')
        self.assertEqual(roy_batty.surname, 'Batty')
        self.assertEqual(roy_batty.email, 'nexus6@gmail.com')

    def test_setattr_email_wrong_input(self):
        """__setattr__ should fail at attempt to set email address that lacks '@' symbol"""
        roy_batty = self.default_person()
        self.assertRaises(WrongInput, setattr, roy_batty, 'email', 'nexus6gmail.com')

    def test_setattr_phone(self):
        """Test if phone numbers are parsed correctly before they are set as 'phone' attribute"""
        roy_batty = self.default_person()

        for num in self.valid_phones:
            setattr(roy_batty, 'phone', num)
            if num in self.valid_phones[:4]:
                self.assertEqual(roy_batty.phone, '668678678')
            else:
                self.assertEqual(roy_batty.phone, '5109999')
                self.assertEqual(roy_batty.phone_area, '42')

    def test_setattr_phone_wrong_input(self):
        """phone_parser should fail with invalid phone numbers"""
        roy_batty = self.default_person()
        invalid = ('66867867', '', 668678678)
        for num in invalid:
            self.assertRaises(WrongInput, setattr, roy_batty, 'phone', num)

    def test_setattr_street(self):
        """While using __setattr__ with 'street' attribute the value should be parsed and two attributes
        ('streetname' and 'streetnumber') should be set consequently"""
        roy_batty = self.default_person()
        for street in self.street_values:
            setattr(roy_batty, 'street', street)
            self.assertEqual(roy_batty.streetname, self.street_values[street][0])
            self.assertEqual(roy_batty.streetnumber, self.street_values[street][1])

    def test_setattr_streetname(self):
        """Test if __setattr__ works correctly with 'streetname' attribute (value should be parsed before setting)"""
        roy_batty = self.default_person()
        street_names = {'baker street': 'Baker St.', 'madison AVENUE': 'Madison Av.',
                        'aleje Jerozolimskie': 'Al. Jerozolimskie', 'Mulholland drive': 'Mulholland Dr.',
                        'broad Road': 'Broad Rd.', 'RED SQUARE': 'Red Sq.'}
        for street in street_names:
            setattr(roy_batty, 'streetname', street)
            self.assertEqual(roy_batty.streetname, street_names[street])
            self.assertEqual(roy_batty.streetnumber, ' ')

    def test_setattr_streetnumber(self):
        """Test if __setattr__ works correctly with 'streetnumber' attribute"""
        roy_batty = self.default_person()
        setattr(roy_batty, 'streetnumber', '10')
        self.assertEqual(roy_batty.streetnumber, '10')
        self.assertEqual(roy_batty.streetname, ' ')

    def test_setattr_street_wrong_input(self):
        """__setattr__ should fail with invalid input"""
        invalid = ('', 'baker street', '10')
        roy_batty = self.default_person()
        for inp in invalid:
            self.assertRaises(WrongInput, setattr, roy_batty, 'street', inp)

    def test_birthday_setattr(self):
        """While using __setattr__ with 'birthday' attribute the value should be parsed and four attributes
        ('birthday', 'year', 'month' and 'year') should be set consequently"""
        birthdays = {'01-10-1968': (dt.date(1968, 10, 1), 1968, 10, 1),
                     '1-10-1968': (dt.date(1968, 10, 1), 1968, 10, 1),
                     '31/10/1968': (dt.date(1968, 10, 31), 1968, 10, 31),
                     '31/01/1968': (dt.date(1968, 1, 31), 1968, 1, 31),
                     '31/1/1968': (dt.date(1968, 1, 31), 1968, 1, 31),
                     '31/12/1968': (dt.date(1968, 12, 31), 1968, 12, 31),
                     '24.12.1000': (dt.date(1000, 12, 24), 1000, 12, 24),
                     '24.12.9999': (dt.date(9999, 12, 24), 9999, 12, 24)}
        roy_batty = self.default_person()
        for date in birthdays:
            setattr(roy_batty, 'birthday', date)
            self.assertEqual(roy_batty.birthday, birthdays[date][0])
            self.assertEqual(roy_batty.year, birthdays[date][1])
            self.assertEqual(roy_batty.month, birthdays[date][2])
            self.assertEqual(roy_batty.day, birthdays[date][3])

    def test_eq(self):
        """Person objects with the same 'personid' attribute are considered equal"""
        roy_batty = self.default_person()
        roy_batty1 = self.default_person(['Roy', 'Batty', 'replic@yahoo.com', '503-456-789'])
        roy_batty2 = self.default_person(['Pris', 'Stratton', 'replic@yahoo.com', '503-456-789'])
        self.assertEqual(roy_batty == roy_batty2, False)
        self.assertEqual(roy_batty == roy_batty1, True)

    def test_ne(self):
        """Person objects with different 'personid' attribute are not considered equal"""
        roy_batty = self.default_person()
        roy_batty1 = self.default_person(['Roy', 'Batty', 'replic@yahoo.com', '503-456-789'])
        roy_batty2 = self.default_person(['Pris', 'Stratton', 'replic@yahoo.com', '503-456-789'])
        self.assertEqual(roy_batty != roy_batty2, True)
        self.assertEqual(roy_batty != roy_batty1, False)

    def test_lt(self):
        """Person objects are compared based on 'personid' attribute"""
        roy_batty = self.default_person()
        roy_batty2 = self.default_person(['Pris', 'Stratton', 'replic@yahoo.com', '503-456-789'])
        self.assertEqual(roy_batty < roy_batty2, True)

    def test_get_age(self):
        """get_age should return age based on 'birthday' attribute. To make tests simpler today's date
        has been replaced with NewDate class method and set to 9-1-2020"""
        roy_batty = self.default_person()
        dt.date = NewDate
        setattr(roy_batty, 'birthday', '8-1-2016')
        self.assertEqual(roy_batty.get_age(), 4)
        setattr(roy_batty, 'birthday', '10-1-2016')
        self.assertEqual(roy_batty.get_age(), 3)

    def test_get_age_no_birthday(self):
        """get_age should fail if 'birthday' attribute is not set"""
        roy_batty = self.default_person()
        self.assertRaises(ValueError, roy_batty.get_age)

    def test_get_age_negative(self):
        """get_age should fail if 'birthday' attribute's value is ahead of current date. To make tests simpler
        today's date has been replaced with NewDate class method and set to 9-1-2020"""
        roy_batty = self.default_person()
        future_dates = ['10-1-2020', '9-1-2021']
        for date in future_dates:
            setattr(roy_batty, 'birthday', date)
            self.assertRaises(ValueError, roy_batty.get_age)

    def test_get_details(self):
        """get_details should return list of all Person's values except for those equal to None"""
        roy_batty = self.default_person()

        # get_details returns only obligatory attributes that are set on initialisation of Person object
        expected = ['Surname: Batty', 'Name: Roy', 'Email: nexus6@gmail.com', 'Phone: 668678678']
        self.assertEqual(roy_batty.get_details(), expected)

        # change in Person's atributes affects the result of get_details
        roy_batty.phone = '668678600'
        expected[3] = 'Phone: 668678600'
        self.assertEqual(roy_batty.get_details(), expected)

        # when additional attributes are set, get_details returns list of all possible attributes
        setattr(roy_batty, 'city', 'los angeles')
        setattr(roy_batty, 'street', '64 baker street')
        setattr(roy_batty, 'birthday', '8-1-2016')
        expected.extend(['Birthday: 2016-01-08', 'City: Los Angeles',
                         'Streetname: Baker St.', 'Streetnumber: 64'])
        self.assertEqual(roy_batty.get_details(), expected)


class TestAddressBook(unittest.TestCase):
    # attributes' names for objects in AddressBook
    keys_to_check = ['name', 'surname', 'email', 'phone', 'city', 'streetname', 'streetnumber',
                     'birthday', 'year', 'month', 'day']

    # values held by 11 identical objects in AddressBook (one object for every attribute name)
    standard_vals = ['roy', 'batty', 'nexus6@gmail.com', '668678678', 'los angeles', 'baker street', '10',
                     '8.1.2016', 2016, 1, 8]

    # values held by 2 objects in AddressBook
    double_vals = ['tony', 'stratton', 'qwerty123@yandex.ru', '3334455', 'pleasantville', 'sunset boulevard', '189']

    # values held by exactly one object in AddressBook
    unique_vals = ['zhora', 'montana', 'foobar@gmail.com', '888000000', 'metropolis', 'broad road', '9',
                   '30/11/1968', 1970, 8, 3]

    # values that no object in AddressBook has
    none_vals = ['norman', 'Bates', 'randommail@gmail.com', '2212345', 'Gotham City', 'downing street', '1',
                 '20.10.1978', 6000, 14, 48]

    # exemplary AddressBook
    people = abook_example()

    def create_values_for_test(self, vals1, vals2=None, keys=keys_to_check):
        """
        Create values for most tests in TestAddressBook class. Values include (1) exemplary AddressBook,
        (2) key-value pairs of attribute names and corresponding attributes that will be uses for adding, modyfying,
        and searching for objects in AddressBook

        Attributes:
                vals1 (list): list of attributes for first 'attribute name - attribute' pair
                vals2 (list): list of attributes for second 'attribute name - attribute' pair
                keys (list): list of attribute names
        """

        abook = copy.deepcopy(self.people)

        pair1 = ({m: n} for m, n in zip(keys, vals1))

        if vals2 is not None:
            pair2 = ({m: n} for m, n in zip(keys, vals2))
            return abook, pair1, pair2

        return abook, pair1

    def test001_add_new_single(self):
        """no duplicates found - user adds new item"""
        people001 = copy.deepcopy(self.people)
        print(len(people001))
        people001.add_new(*self.none_vals[:4])
        self.assertEqual(len(people001), 23)
        self.assertIsInstance(people001[-1], Person)

    @patch('builtins.input', return_value='n')
    def test002_add_new_multiple_no(self, mock_input):
        """duplicates found - user chooses not to add anything"""
        people002 = copy.deepcopy(self.people)
        length = len(people002)
        people002.add_new(*self.standard_vals[:4])
        self.assertEqual(len(people002), length)

    @patch('builtins.input', return_value='y')
    def test003_add_new_multiple_yes(self, mock_input):
        """duplicates found - user adds new item"""
        people003 = copy.deepcopy(self.people)
        length = len(people003)
        people003.add_new(*self.standard_vals[:4])
        self.assertEqual(len(people003), length + 1)

    def test004_clear_base(self):
        """remove all antries from AddressBook"""
        people004 = copy.deepcopy(self.people)
        people004.clear_base()
        self.assertEqual(len(people004), 0)

    def test005_sorting(self):
        """sort AddressBook by objects' attributes"""
        people005 = copy.deepcopy(self.people)
        for key in self.keys_to_check:
            shuffle(people005)
            people005.sorting(key)
            self.assertTrue(all((getattr(people005[i], key) is None, getattr(people005[i], key)) <=
                                (getattr(people005[i + 1], key) is None, getattr(people005[i], key))
                                for i in range(len(people005) - 1)))
            people005.sorting(key, reverse=True)
            self.assertTrue(all((getattr(people005[i + 1], key) is not None, getattr(people005[i], key)) >=
                                (getattr(people005[i], key) is not None, getattr(people005[i], key))
                                for i in range(len(people005) - 1)))

    def test006_search_base_none(self):
        """search_base should return None for non-existent objects"""

        people006, pairs_to_check = self.create_values_for_test(self.none_vals)

        for pair in pairs_to_check:
            self.assertEqual(people006.search_base(**pair), None)

    def test007_search_base_multiple(self):
        """search_base should return list of objects if given criteria match multiple objects"""

        people007, pairs_to_check = self.create_values_for_test(self.standard_vals)

        for pair in pairs_to_check:
            self.assertEqual(len(people007.search_base(**pair)), 11)
            self.assertIsInstance(people007.search_base(**pair), list)

    def test008_search_base_one_result(self):
        """if exactly one object meets given criteria, search_base should return this object"""

        people008, pairs_to_check = self.create_values_for_test(self.unique_vals)

        for pair in pairs_to_check:
            self.assertIsInstance(people008.search_base(**pair), Person)

    def test_009_removal_single(self):

        people009, pairs_to_remove = self.create_values_for_test(self.unique_vals)

        for pair in pairs_to_remove:
            people009.removal(**pair)
            self.assertEqual(people009.search_base(**pair), None)

    def test_010_removal_not_found(self):
        """removal should raise ItemNotFound exception if item in question doesn't exist"""

        people010, pairs_to_remove = self.create_values_for_test(self.none_vals)
        for pair in pairs_to_remove:
            self.assertRaises(ItemNotFound, people010.removal, **pair)

    @patch('builtins.input', return_value='n')
    def test_011_removal_multiple_no(self, mock_input):
        """duplicates found = user refuses to remove anything"""

        people011, new_pairs = self.create_values_for_test(self.standard_vals)

        for pair in new_pairs:
            length = len(people011)
            people011.removal(**pair)
            self.assertEqual(len(people011), length)
            self.assertEqual(len(people011.search_base(**pair)), 11)

    def test_012_removal_multiple_wrong_input_no(self):
        """duplicates found = firstly, user enters wrong input, then refuses to remove anything"""

        people012, new_pairs = self.create_values_for_test(self.standard_vals)

        for pair in new_pairs:
            with patch('builtins.input', side_effect=['12', 'qwerty', 'n']):
                length = len(people012)
                people012.removal(**pair)
                self.assertEqual(len(people012), length)
                self.assertEqual(len(people012.search_base(**pair)), 11)

    @patch('builtins.input', return_value='1')
    def test_012_removal_multiple_remove_one(self, mock_input):
        """duplicates found - user removes one of them"""

        people012, pairs = self.create_values_for_test(self.standard_vals)

        for pair in pairs:
            length = len(people012)
            people012.removal(**pair)
            self.assertEqual(len(people012), length - 1)

    @patch('builtins.input', return_value='a')
    def test_013_removal_multiple_all(self, mock_input):
        """duplicates found - user removes all of them"""

        people013, pairs = self.create_values_for_test(self.standard_vals)
        people013.removal(name='roy')
        for pair in pairs:
            self.assertEqual(people013.search_base(**pair), None)


if __name__ == '__main__':
    with suppress_stdout():
        unittest.main()
