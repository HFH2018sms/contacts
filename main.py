#!/home/ahouts/.conda/envs/hfh2018sms/bin/python

import sys
import json


class Contact:
    def __init__(self):
        self.number = ""
        self.name = ""
        self.geolocation = ""
        self.contacts = []

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_number(self, number):
        self.number = number

    def get_number(self):
        return self.number

    def get_geolocation(self):
        return self.geolocation

    def set_geolocation(self, loc):
        self.geolocation = loc

    def add_contact(self, number):
        self.contacts.append(number)

    def remove_contact(self, number):
        for i, n in enumerate(self.contacts):
            if n == number:
                self.contacts.pop(i)
                return

    def to_json(self):
        data = {
            "number": self.number,
            "name": self.name,
            "geolocation": self.geolocation,
            "contacts": self.contacts
        }
        return data

    @staticmethod
    def from_json(data):
        contact = Contact()
        contact.geolocation = data["geolocation"]
        contact.name = data["name"]
        contact.number = data["number"]
        contact.contacts = data["contacts"]
        return contact


class GlobalContacts:
    def __init__(self):
        self.contacts = {}

    def add_contact(self, contact):
        assert(isinstance(contact, Contact))
        self.contacts[contact.get_number()] = contact

    def get_contact(self, number):
        return self.contacts[number]

    def to_json(self):
        dat = {}
        for key, val in self.contacts.items():
            dat[key] = val.to_json()
        return dat

    @staticmethod
    def from_json(data):
        contacts = GlobalContacts()
        for _, val in data.items():
            contacts.add_contact(Contact.from_json(val))
        return contacts


def first_time_setup(data, gdata, cmd, number):
    to_display = ""
    data["state"] = "first_time_setup"
    if "setup_state" not in data or data["setup_state"] == 0:
        to_display = "Welcome to contacts! Please enter your name..."
        data["setup_state"] = 1
    elif data["setup_state"] == 1:
        if cmd == "":
            to_display = "Please input a name..."
            data["setup_state"] = 1
        else:
            to_display = "Thank you " + " ".join(cmd) + ", setup is now complete."
            data["setup_state"] = 2
            new_c = Contact()
            new_c.name = " ".join(cmd)
            new_c.number = number
            if "contacts" not in gdata:
                gdata["contacts"] = GlobalContacts()
            gdata["contacts"].add_contact(new_c)
            data["state"] = "main"
    else:
        data["setup_state"] = 0
    return to_display


def help_text(cmd):
    if len(cmd) < 2:
        return "* Contacts *\ncommands: add, list, search, exit.\ntype \"help <command name>\" for help with a command"
    if cmd[1] == "exit":
        return "usage: \"exit\", exits the contacts app"
    elif cmd[1] == "add":
        return "usage: add <phone number>, lists your contacts"
    elif cmd[1] == "search":
        return "usage: search <name>, lists people with that name"
    elif cmd[1] == "list":
        return "usage: list, lists your contacts"
    else:
        return "commands: add, list, search, exit.\ntype \"help <command name>\" for help with a command"


def list_branch(data, gdata, cmd, number):
    data["state"] = "list"
    me = gdata["contacts"].get_contact(number)
    my_contacts = me.contacts
    for cn in my_contacts:
        contact = gdata["contacts"].get_contact(cn)
        



def main_sequence(data, gdata, cmd, number):
    if len(cmd) == 0:
        exit_sequence("Welcome to Contacts...", data, gdata, False)
    branch = cmd[0].lower()
    if branch == "help":
        exit_sequence(help_text(cmd), data, gdata, False)
    elif branch == "add":
        exit_sequence("Exiting Contacts...", data, gdata, True)
    elif branch == "search":
        exit_sequence("Exiting Contacts...", data, gdata, True)
    elif branch == "list":
        data["list_index"] = 0
        list_branch(data, gdata, cmd, number)
    elif branch == "exit":
        exit_sequence("Exiting Contacts...", data, gdata, True)
    else:
        previous_data["state"] = "main"
        exit_sequence(branch + " is an invalid command...", data, gdata, False)


def exit_sequence(display, new_dat, global_dat, exit_prog):
    if "contacts" in global_dat and isinstance(global_dat["contacts"], GlobalContacts):
        global_dat["contacts"] = global_dat["contacts"].to_json()
    res = {
        "to_display": display,
        "new_data": json.dumps(new_dat),
        "global_data": json.dumps(global_dat),
        "exit": exit_prog
    }
    res_json = json.dumps(res)
    print(res_json)
    exit(0)


if __name__ == "__main__":
    input_data = json.loads(sys.argv[1])
    my_number = input_data["number"]
    command = input_data["command"]
    arguments = input_data["args"]
    previous_data = input_data["prev_data"]
    global_data = input_data["global_data"]

    if previous_data == "":
        previous_data = {}
    else:
        previous_data = json.loads(previous_data)
    if global_data == "":
        global_data = {}
    else:
        global_data = json.loads(global_data)
        if "contacts" in global_data:
            global_data["contacts"] = GlobalContacts.from_json(global_data["contacts"])

    if previous_data == {}:
        res = first_time_setup(previous_data, global_data, arguments, my_number)
        exit_sequence(res, previous_data, global_data, False)
    if previous_data["state"] == "first_time_setup":
        res = first_time_setup(previous_data, global_data, arguments, my_number)
        exit_sequence(res, previous_data, global_data, False)
    if previous_data["state"] == "main":
        main_sequence(previous_data, global_data, arguments, my_number)
    if previous_data["state"] == "list":
        list_branch(previous_data, global_data, arguments, my_number)
    previous_data["state"] = "main"
    exit_sequence("invalid state, resetting...", previous_data, global_data, False)
