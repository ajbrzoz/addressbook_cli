"""This module contains AddressBook class used for storing, adding and modifying entries"""

import pickle
import textwrap as tw
import time

from addressbook.ab_person import *
from addressbook.ab_helpers import *


class AddressBook(list):
    """Class for creating and modifying the AddressBook"""

    def __init__(self):
        super().__init__()
        self.filename = None    # Used when working with opened file

    @staticmethod
    def check(obj):
        if not isinstance(obj, Person):
            raise TypeError(obj)
        else:
            return obj

    def append(self, obj):
        return super().append(self.check(obj))

    def insert(self, index, obj):
        return super().insert(index, self.check(obj))

    def extend(self, iterable):
        return super().extend([self.check(i) for i in iterable])

    def __add__(self, other):
        return super().__add__(self.check(other))

    def __setitem__(self, index, obj):
        if isinstance(index, slice):
            return super().__setitem__(index, [self.check(o) for o in obj])
        else:
            return super().__setitem__(index, self.check(obj))

    def add_new(self, name, surname, email, phone):
        """Add a new person to the AddressBook by creating a new Person instance.
        Before adding a new item the function checks if there is not anybody
        with such a name + surname combination in the AddressBook. If so, the user is asked whether he/she wants to
        add the person anyway.

        Attributes:
            name (str): Person's name
            surname (str): Person's surname
            email (str): Person's email address
            phone (str): Person's phone number
        """
        c = str(surname.title() + "_" + name.title())

        # with an empty list there's no need to check for duplicates
        if len(self) == 0:
            super().append(Person(name, surname, email, phone))
            print('{0} {1} has been added to the base.'.format(name.title(), surname.title()))
        else:
            item = self.search_base(personid=c)
            try:
                # no items with similar name and surname found
                if item is None:
                    super().append(Person(name, surname, email, phone))
                    print('{0} {1} has been added to the base.'.format(name.title(), surname.title()))
                # duplicates found
                else:
                    while True:
                        ask = input(
                            'There is already a person called {0} {1} in our base. '
                            '\nDo you want to add such a person anyway? y/n '.format(
                                name.title(), surname.title())).lower()
                        if ask in ('y', 'yes'):
                            super().append(Person(name, surname, email, phone))
                            print('{0} {1} has been added to the base.'.format(name.title(), surname.title()))
                            break
                        elif ask in ('n', 'no'):
                            break
                        else:
                            print('Wrong input.')
                            continue
            # invalid format of either email or phone
            except WrongInput as ex:
                print(str(ex) + ' The item cannot be added.')

    def clear_base(self):
        """Remove all elements from the AddressBook"""
        self.clear()
        print('The AddressBook is empty.')

    def how_many(self):
        """Show the number of elements in the AddressBook"""
        if len(self) > 0:
            print('There are {0} people in your AddressBook.'.format(str(len(self))))
        else:
            print('The AddressBook is empty.')

    def sorting(self, att, reverse=None):
        """Sort the AddressBook by a person's key value

        Attributes:
            att (str): Person's key
        """
        if reverse is None:
            return self.sort(key=lambda x: (x.__getattribute__(att) is None, x.__getattribute__(att)))
        return self.sort(key=lambda x: (x.__getattribute__(att) is None, x.__getattribute__(att)), reverse=True)

    def search_base(self, **kwargs):
        """Search through the AddressBook to find the item with the specified key value
        (or a list of items in case of multiple matching returns. Since the 'search_base' uses the 'search' function,
        which is based on binary search, the AddressBook's items are sorted by the keyword attribute given in **kwargs
        before the search begins.

        Attributes:
            **kwargs (keyword=str): Key and value of the person being looked for
        """

        for (k, v) in kwargs.items():
            capit = ('name', 'surname', 'city')
            if k in capit:
                v = v.title()
            elif k == 'streetname':
                v = street_parser(v, '')[0]
            elif k == 'phone':
                v = phone_parser(v)[0]
            elif k == 'birthday':
                y, m, d = date_parser(v)
                v = dt.date(y, m, d)
            elif k in ['year', 'month', 'day']:
                v = int(v)
            self.sorting(k)
            # found items (None, a Person object or list of objects)
            found = search(self, v, k)
            return found

    def show_all_results(self):
        """Print out the details of all the people listed in the AddressBook."""

        twrapper = tw.TextWrapper(width=80, initial_indent='\t', subsequent_indent='\t',
                                  break_long_words=False)

        ix = 1
        for s in range(len(self)):
            print(' <{0}>  '.format(ix))
            for line in twrapper.wrap(str(self[s].get_details()).replace(',',
                        ' | ').replace("'", '').replace('[', '').replace(']', '')):
                print(line)
            print()
            ix += 1

    def removal(self, **kwargs):
        """Remove an item (with a key value specified by user) from the AddressBook.
        In order to remove the item, it checks if there is a person with such a key value in a list.
        If no person is found, the function raises ItemNotFound exception.
        If the address book is empty, it returns EmptyBase exception.
        In case of multiple matching returns, the user is asked to choose one them by selecting
        the corresponding number.

        Attributes:
            **kwargs (keyword=str): Key and value of the person to be removed
        """

        # found items (None, a Person object or list of objects)
        found = self.search_base(**kwargs)

        if found is None:
            raise ItemNotFound("The element you're looking for")
        try:
            # single item found
            if isinstance(found, Person):
                self.remove(found)
            # multiple items found
            elif len(found) > 1:
                raise Multiple(len(found))
        except Multiple as ex:
            print(ex)
            for i, j in enumerate(found):
                print(str(i + 1) + ': \n' + tw.fill(str(j.get_details()), width=80))
                print("")
            while True:
                ask = input("Which person would you like to remove? "
                            "\nChoose the corresponding number. "
                            "\nIf you don't want to remove any of the entries, type in 'N' "
                            "\nIf you want to remove all of them, type in A ").lower()
                try:
                    if ask in ('n', 'no'):
                        break
                    elif ask == 'a':
                        for j in found:
                            self.remove(j)
                        print("All requested elements have been removed.")
                        break
                    elif int(ask) in range(1, len(found) + 1):
                        self.remove(found[int(ask) - 1])
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("{0} is not a proper input. Choose the person's number.".format(ask))

    def pickle_base(self, filename=None):
        """Save AddressBook as a pickle file.

        Attributes:
            filename (str) - File saving name
        """

        if filename is None:
            # default filename containing saving time
            abook_name = 'abook' + time.strftime('%Y-%m-%d') + '.pkl'
        else:

            abook_name = filename + '.pkl'

        abook_file = open(abook_name, 'wb')
        pickle.dump(self, abook_file, 2)
        abook_file.close()

        self.filename = abook_name

    def pickle_changes(self):
        """Save changes made to an opened file."""

        base_file = open(self.filename, 'wb')
        pickle.dump(self, base_file, 2)
        base_file.close()
