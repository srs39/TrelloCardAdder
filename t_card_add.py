# Author: Samantha Shoecraft
# Date: 12/19/2018
#
# Details:
# A program to add card with comments and labels to trello board y on column x
# If board, column or labels do not exist, they are added to the user's account
# runs from command line:
# python3 add_trello_card.py --key your_key --token your_token --card "Test card"
# --label "Test label, Test label2, Test label3" --comment "Test comment" --board "Test board" --column "Test column"
#
# The flags card, label, board, and column refer to the names of the objects, not their id numbers
# Multiple labels can be added, but must be separated by commas the default limit is 50 labels
# All flags must be used in order for program to work properly
#
# To do:
#   unit tests

import sys
import getopt
import json
import requests
import random

ARG_NUM = 7


def main(argv):
    opts, api_key, api_token, card_title, label_title, user_comment, board_name, column_name = \
        ['', '', '', '', '', '', '', '']
    # Gets arguments from the command line and saves them in a multidimensional list.
    # If a flag is not recognized, it wil throw and exception and program will exit.
    try:
        opts, args = getopt.getopt(argv, "", ["key=", "token=", "card=", "label=", "comment=", "board=", "column="])
    except getopt.GetoptError:
        print("One or more options is not recognized")
        quit()

    # Checks that there are the right number of arguments, and will exit if too few
    if len(opts) < ARG_NUM:
        print("wrong number of arguments")
        quit()

    # Takes arguments and assigns them to the appropriate variable
    for opt, arg in opts:
        if opt == "--key":
            api_key = arg
        elif opt == "--token":
            api_token = arg
        elif opt == "--card":
            card_title = arg
        elif opt == "--label":
            label_title = arg
        elif opt == "--comment":
            user_comment = arg
        elif opt == "--board":
            board_name = arg
        elif opt == "--column":
            column_name = arg

    # calls to functions to get appropriate variables
    labels = label_title.split(', ')
    member_id = get_member_id(api_token, api_key)

# This method takes in token and key and returns the members id number associated with the token
# If the token or key are incorrect, it will throw an exception and exit
def get_member_id(token, key):
    try:
        url = 'https://api.trello.com/1/tokens/%s?token=%s&key=%s' % (token, token, key)
        r = requests.get(url)
        member_dict = json.loads(r.text)
        mem_id = member_dict["idMember"]
        return mem_id

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: Key or Token incorrect")
        quit()
