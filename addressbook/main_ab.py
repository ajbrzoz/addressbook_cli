#!/bin/env python

# Written by Anna Brzozowska, June 2016.

"""This the main module of AddressBook 1.0.

AddressBook 1.0 is a simple, (relatively) easy to use command-line contact manager that helps to
keep track of your contacts, including email addresses, phones, addresses and birthdays. It enables
users to create their own address books, save them (in pickle format) and restore data from existing ones.
Options include adding, modifying and removing entries, as well as sorting and searching through them.

"""

import glob
import shutil
from time import localtime, strftime

from addressbook.ab_abook import *


class MainApp(object):
    """Class for creating and navigating through program interface."""

    def __init__(self):

        self.term_w = shutil.get_terminal_size((80, 20))[0]  # terminal size

        self.abook = AddressBook()  # AddressBook (base of contacts) to work with
        self.book_opened = False  # True when working with opened file
        self.before_abook = self.abook  # used for indicating if user has made any changes

        # names of attributes that can be set for every object in AddressBook combined with
        # corresponding prompts for input
        self.events = {'1': {'name': '>> Name: '}, '2': {'surname': '>> Surname: '},
                       '3': {'email': '>> Email: '}, '4': {'phone': '>> Phone: '},
                       '5': {'birthday': '>> Birthday [d-m-y or d/m/y or d.m.y]: '},
                       '6': {'year': '>> Year of Birth: '}, '7': {'month': '>> Month of Birth: '},
                       '8': {'day': '>> Day of Birth: '}, '9': {'city': '>> City: '},
                       '10': {'streetname': '>> Street Name: '}, '11': {'streetnumber': '>> Street Number: '},
                       '12': {'street': '>> Street (name and number): '}}

        # string to be printed when user chose to modify/remove/sort or search through entries
        self.events_string = '''\n
                    1 - Name\t2 - Surname\t3 - Email\t4 - Phone\n
                    5 - Birthday\t6 - Year\t7 - Month\t8 - Day\n
                    9 - City\t10 - Street Name\t11 - Street Number\n
                    12 - Back to AddressBook Options\t13 - Back to Main Menu\t14 - Exit\n
                    \n
                    '''.center(self.term_w)

        self.action_start()  # go to Main Menu

    def intro(self, mode):
        """Print introduction for corresponding menus"""

        msg = ''
        modes = {"start": "  Welcome to AddressBook 1.0  ", "next": "  AddressBook Options  ",
                 "personal": "  Single Entry Options  ", "search": "  Search Options  ",
                 "sort": "  Sorting Options  ", "add": "  Adding New Entry  ",
                 "remove": "  Removal Options  ", "save": "  Save Options  "}
        if mode in modes:
            msg = modes[mode]

        print()
        print("{:-^{}s}".format(msg, self.term_w - 5))  # adjust intro to terminal size
        print()

    def action_start(self):
        """Main Menu options: creating new base, open existing one or exiting"""

        self.intro('start')

        while True:
            s = '''\n
            \t1 - New AddressBook\t\t2 - Open AddressBook\t\t3 - Exit
            \n
            '''
            print(s)
            ask_for_action = input(">> {}".format(" What do you want to do? Choose the number: "))

            # create new AddressBook
            if ask_for_action == '1':
                print(">> New AddressBook created.")
                self.action_next()

            # open AddressBook
            elif ask_for_action == '2':

                cwd = os.getcwd()
                find_pkl(cwd)  # find .pkl files in current working directory and print their details

                while True:

                    ask_for_fname = input("\n>> Enter filename/ filepath: ")

                    # if user enters path without filename, show .pkl files in given directory
                    if os.path.isdir(ask_for_fname):
                        find_pkl(ask_for_fname)
                        os.chdir(ask_for_fname)

                    # if user chooses filename of existing, non-empty, .pkl file, this file is assigned
                    # to self.abook
                    else:
                        try:
                            book_to_open = self.action_open(ask_for_fname)
                            if self.book_opened is True:
                                self.abook = book_to_open
                                self.action_next()
                        except EmptyFile as ex:
                            print(ex)
                        except FormatError as ex:
                            print(ex)
                        self.action_start()

            elif ask_for_action == '3':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(ask_for_action))

    def action_next(self):
        """AddressBook options for working with a newly-created or opened AddressBook:
        Show All Results - print out details of all contacts in the AddressBook
        Search - go to search menu
        Sort - go to sorting menu
        Add New Entry - go to menu for adding new contacts
        Delete Entry - go to menu removing existing contacts
        Save - save changes made to opened file
        Save As - save file after choosing its name and saving location
         """

        self.intro('next')

        print()
        self.abook.how_many()  # shows number of entries in AddressBook

        while True:
            s = '''\n
                1 - Show All Results\t\t2 - Search\t\t3 - Sort\n
                4 - Add New Entry\t\t5 - Delete Entry\n
                6 - Save\t7 - Save As\t8 - Back to Main Menu\t\t9 - Exit
                \n
                '''.center(self.term_w)
            print(s)
            event = input(">> {}".format(" What do you want to do? Choose the number: "))

            if event == '1':
                self.abook.show_all_results()
                self.action_next()
            elif event == '2':
                self.action_search()
            elif event == '3':
                self.action_sort()
            elif event == '4':
                self.action_add()
            elif event == '5':
                self.action_remove()
            elif event == '6':
                if self.abook.filename is None:
                    print(">> This option is available only for already existing AddressBooks.\n"
                          ">> In order to save a newly-created AddressBook choose '7'.")
                else:
                    self.abook.pickle_changes()
                    print(">> The AddressBook has been saved.")
            elif event == '7':
                name = input(">> Enter filename/filepath \n"
                             ">> or press 'd' if you want to save file with default name: ").lower()
                if name == 'd':
                    name = None
                self.abook.pickle_base(filename=name)
                print(">> The AddressBook has been saved.")
            elif event == '8':
                self.action_start()
            elif event == '9':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(event))

    def action_search(self):
        """Search options"""

        self.intro('search')

        # if AddressBook is empty, print a message and go back to AddressBook options
        if len(self.abook) == 0:
            print("\n>> You cannot search through an empty base.")
            self.action_next()

        while True:

            print(self.events_string)
            event = input(">> {}".format("Choose search criteria: "))

            # user chooses search criteria and specifies the values he/she wants to find,
            # each category is connected with a number ranging from 1 to 11
            if event in [str(n) for n in range(1, 12)]:
                for key, val in self.events[event].items():
                    while True:
                        inp = input(val)
                        to_find = {key: inp}
                        with exc_catcher():
                            result = self.abook.search_base(**to_find)
                            if result is None:
                                print(">> No items found.")
                                self.action_next()
                            elif isinstance(result, Person):
                                print(">> 1 item found.")
                                print(tw.fill(str(result.get_details()), width=80))

                            else:
                                print(">> {} items found.".format(len(result)))
                                for i, j in enumerate(result):
                                    print(str(i + 1) + ': \n')
                                    print(tw.fill(str(j.get_details()), width=80), sep=' | ')
                                    print()
                            self.action_person(result)
            elif event == '12':
                self.action_next()
            elif event == '13':
                self.action_start()
            elif event == '14':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(event))

    def action_sort(self):
        """Sorting options"""

        self.intro('sort')

        # if AddressBook is empty, print a message and go back to AddressBook options
        if len(self.abook) == 0:
            print("\n>> You cannot sort an empty base.")
            self.action_next()

        while True:
            print(self.events_string)
            event = input(">> {}".format("Choose sorting criteria: "))

            # user chooses sorting criteria and specifies the values he/she wants to find,
            # each category is connected with a number ranging from 1 to 11
            if event in [str(n) for n in range(1, 12)]:
                for key in self.events[event].keys():
                    order = "ascending"
                    is_reversed = input(">> Press 'd' to sort in descending order\n"
                                        "   Press any other key to sort in ascending (default) order: ").lower()
                    if is_reversed == 'd':
                        self.abook.sorting(key, reverse=True)
                        order = "descending"
                    else:
                        self.abook.sorting(key)
                    print(">> The base has been sorted by '{0}' attribute in {1} order.".format(key, order))
                    self.action_next()
            elif event == '12':
                self.action_next()
            elif event == '13':
                self.action_start()
            elif event == '14':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(event))

    def action_remove(self):
        """Options for removing entries from AddressBook"""

        self.intro('remove')

        # if AddressBook is empty, print a message and go back to AddressBook options
        if len(self.abook) == 0:
            print("\n>> There are no items to remove.")
            self.action_next()

        print(">> You need to choose attribute and value of the item you want to remove.")

        while True:

            print(self.events_string)

            event = input(">> {}".format("Choose attribute, then enter value: "))

            # user chooses removal criteria and specifies the values he/she wants to find,
            # each category is connected with a number ranging from 1 to 11
            if event in [str(n) for n in range(1, 12)]:
                for key, val in self.events[event].items():
                    inp = input(val)
                    to_find = {key: inp}
                    with exc_catcher():
                        self.abook.removal(**to_find)
                        print(">> The item has been successfully removed.")
                        self.action_next()
            elif event == '12':
                self.action_next()
            elif event == '13':
                self.action_start()
            elif event == '14':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(event))

    def action_add(self):
        """Adding new entries"""

        self.intro('add')

        before_len = len(self.abook)

        name_inp = input('>> Name: ').capitalize()
        surname_inp = input('>> Surname: ').capitalize()
        email_inp = None
        while True:
            try:
                email_inp = input('>> Email: ')
                email_inp = email_valid(email_inp)
                break
            except WrongInput as ex:
                print(ex)
        while True:
            phone_inp = input('>> Phone: ')
            with exc_catcher():
                self.abook.__append__(name_inp, surname_inp, email_inp, phone_inp)
                break

        # if no new entry has been added, go back to AddressBook options
        if len(self.abook) == before_len:
            self.action_next()

        # if new entry has been successfully added, user decides whether to proceed to entry edition options
        # or go back to AddressBook options
        else:
            self.action_person(self.abook[-1])

    def action_person(self, entry):
        """After adding a new entry or getting search results, user is asked if he/she wants to modify or remove
         the entry (or one of entries in case of multiple results) or leave it without changes.
         Depending on user's decision, the program proceeds to Single Entry Options or returns to
         AddressBook options"""

        self.intro('personal')

        person_event = input(">> Do you want to modify/remove this entry (one of entries above)?\n"
                             ">> Press 'y' to continue, any other key to go back: ").lower()
        if person_event in ['y', 'yes']:
            if isinstance(entry, Person):
                item = entry
                self.action_person_edit(item)
            else:
                for i, j in enumerate(entry):
                    ix = i + 1
                    print(str(ix) + ': \n' + tw.fill(str(j.get_details()), width=80))
                    print("")
                while True:
                    ask = input(">> Which entry would you like to modify/remove? "
                                "\n>> Choose the corresponding number. "
                                "\n>> If you don't want to remove any of the entries, type in 'N' "
                                ).lower()
                    try:
                        if ask in ('n', 'no'):
                            self.action_next()
                        elif int(ask) in range(1, len(entry) + 1):
                            item = entry[int(ask) - 1]
                            self.action_person_edit(item)
                        else:
                            raise ValueError
                    except ValueError:
                        print(">> {0} is not a proper input. Choose the person's number.".format(ask))
        else:
            self.action_next()

    def action_person_edit(self, item):
        """Single Entry Options allow to change/set entry's attributes"""

        self.intro('personal')

        while True:
            s = '''\n
                1 - Name\t2 - Surname\t3 - Email\t4 - Phone\t5 - Birthday\n
                6 - City\t7 - Street Name\t\t8 - Street Number\t9 - Street\n
                10 - Get Age\n
                11 - Back to AddressBook\t12 - Back to Main Menu\t\t13 - Exit\n
                \n
                '''.center(self.term_w)
            print(s)
            event = input(">> {}".format(" What attribute do you want to change/set? Choose the number: "))

            # user chooses a category and specifies new value that will be set,
            # each category is connected with a number ranging from 1 to 9
            if event in [str(n) for n in range(1, 10)]:
                for key, val in self.events[event].items():
                    while True:
                        inp = input(val)
                        with exc_catcher():
                            setattr(item, key, inp)
                            print(">> The item has been successfully modified.")
                            self.action_person_edit(item)
            elif event == '10':
                try:
                    print(">> {0.name} {0.surname} is {1} years old.".format(item, item.get_age()))
                except ValueError as ex:
                    print(">> {}".format(ex))
                self.action_person_edit(item)
            elif event == '11':
                self.action_next()
            elif event == '12':
                self.action_start()
            elif event == '13':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(event))

    def action_open(self, fname):
        """Opening existing AddressBook"""

        try:
            # raise exception if extension of the file chosen by user is not .pkl
            if not fname.endswith('.pkl'):
                raise FormatError
            # raise exception for empty files
            if os.path.getsize(fname) == 0:
                raise EmptyFile
            pkl_file = open(fname, 'rb')
            abook = pickle.load(pkl_file)
            abook.filename = fname
            pkl_file.close()
            self.book_opened = True  # indicates that a file has been opened
            return abook
        # if file is not found, ask if user wants to create new AddressBook
        except FileNotFoundError:
            while True:
                ask = input(">> No such file. Do you want to create new AddressBook?\n"
                            ">> Press 'y' to continue, any other key to go back: ").lower()
                if ask in ['y', 'yes']:
                    abook = AddressBook()
                    print(">> New AddressBook created.")
                    self.book_opened = True
                    return abook
                else:
                    print(">> No AddressBook created.")
                    self.action_start()

    def action_save(self):
        """Saving options"""

        self.intro("save")

        s = '''\n
            1 - Save\t\t2 - Save As\t\t3 - Exit
            \n
            '''.center(self.term_w)
        print(s)
        event = input(">> {}".format(" What do you want to do? Choose the number: "))

        while True:
            if event == '1':
                self.abook.pickle_changes()
                print("The AddressBook has been saved.")
                self.action_next()
            elif event == '2':
                name = input(">> Enter filename/filepath \n"
                             ">> or press 'd' if you want to save file with default name: ").lower()
                if name == 'd':
                    name = None
                self.abook.pickle_base(filename=name)
                print("The AddressBook has been saved.")
                self.action_next()
            elif event == '3':
                self.action_exit()
            else:
                print(">> '{}' is not a proper input. Try again.".format(event))

    def action_exit(self):
        """Exit options"""

        # if any changes have been made, user decides whether to save them before exiting
        if self.abook != self.before_abook:
            save_ask = input("The Addressbook has been changed. Do you want to save it?\n"
                             ">> If so, press 's', if you don't - press any other key: ").lower()
            if save_ask == 's':
                self.action_save()

        print("\n>> ...Exiting...\n")
        sys.exit()


def find_pkl(fname, directory=None):
    if os.path.isdir(fname):
        directory = fname

    elif os.path.isfile(fname):
        directory = os.path.dirname(fname)

    dir_show = ">> Current directory: {}\n".format(directory)
    print(dir_show, "-" * len(dir_show))

    filenames = glob.glob(os.path.join(directory, "*.pkl"))

    if len(filenames) == 0:
        print("\n>> No AddressBooks found in this location.")
    else:
        print("\n>> {} AddressBooks found in this location:".format(len(filenames)))

        heading = "\n\t-----  Filename  -----  Size  -----  Last modified  -----\n"
        print(heading)

        for name in filenames:
            short_name = os.path.basename(name)
            size = human_size(os.stat(name).st_size)
            modified = strftime("%Y-%m-%d %H-%M", localtime(os.stat(name).st_mtime))
            print("\t{:^22s}{:^8s}{:^27s}".format(short_name, size, modified))


if __name__ == '__main__':
    with keyboard_catcher():
        MainApp()
