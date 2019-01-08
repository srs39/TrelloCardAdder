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
    boards = get_member_boards(member_id, api_token, api_key)
    board_id = get_board_id(boards, board_name, api_token, api_key)
    label_id = get_label_id(board_id, labels, api_token, api_key)
    column_id = get_column_id(board_id, column_name, api_token, api_key)
    add_new_card(column_id, card_title, label_id, user_comment, api_token, api_key)
    print("Request was successful")

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

# This method takes in mem_id, token and key and returns the boards connected with that user
# If member id, token or key are invalid an error message will occur and program will exit
def get_member_boards(mem_id, token, key):
    try:
        url = "https://api.trello.com/1/members/%s/idBoards?key=%s&token=%s" % (mem_id, key, token)
        r = requests.get(url)
        boards_dict = json.loads(r.text)
        return boards_dict

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: could not get boards")
        quit()


# This method takes in a list of board id numbers, the name of the target board, the key and the token
# It returns the board id number for the target board
# If the target board is not found, a new board is created
# if board ids, token or key are invalid, an error message will print and the program will exit
def get_board_id(boards, board_name, token, key):
    try:
        for b in boards:
            url = "https://api.trello.com/1/boards/%s/name?key=%s&token=%s" % (b, key, token)
            r = requests.get(url)
            b_id = json.loads(r.text)
            if b_id['_value'] == board_name:
                return b

        return add_new_board(board_name, token, key)

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: incorrect board id")
        quit()


# This method takes in the board_name, token and key and returns the id number of the new board created
# If token or key are invalid or if the board_name is an empty string an error message will print and program will exit
def add_new_board(board_name, token, key):
    try:
        url = "https://api.trello.com/1/boards/"
        querystring = {"name": board_name, "defaultLabels": "true", "defaultLists": "false", "keepFromSource": "none",
                       "prefs_permissionLevel": "public", "prefs_voting": "disabled", "prefs_comments": "members",
                       "prefs_invitations": "members", "prefs_selfJoin": "true", "prefs_cardCovers": "true",
                       "prefs_background": "blue", "prefs_cardAging": "regular", "key": key, "token": token}
        response = requests.request("POST", url, params=querystring)
        new_board = json.loads(response.text)
        return new_board["id"]

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: new board unsuccessful")
        quit()


# This program takes in the board id, a list of label names, the token and the key and returns list of label ids
# If labels are not already associated with the board, a new label will be added
# Will add blank label if no label specified
def get_label_id(board_id, labels, token, key):
    existing_labels = []
    new_labels = []
    try:
        url = 'https://api.trello.com/1/boards/%s/labels?fields=all&limit=50&key=%s&token=%s' % (board_id, key, token)
        r = requests.get(url)
        user_labels = json.loads(r.text)
        for label in range(len(labels)):
            for l in user_labels:
                if l['name'] == labels[label]:
                    existing_labels.append(l['id'])
            if (len(new_labels)+len(existing_labels)) < len(labels):
                new_labels.append(labels[label])
        if len(new_labels) > 0:
            new_label_id = add_new_labels(board_id, new_labels, token, key)
            if len(existing_labels) > 0:
                for ex_label in existing_labels:
                    new_label_id.append(ex_label)
            return new_label_id

        else:
            return existing_labels

    except (requests.RequestException, json.JSONDecodeError):
        print("Label id Error")
        quit()


# This method takes in a board id, a list of label names, the token and the key
# It returns a list of new label ids that have been created with a random color
# If label name, the token or the key are invalid, an error message will print and it will exit program
def add_new_labels(board_id, labels, token, key):
    label_colors = ['yellow', 'purple', 'blue', 'red', 'green', 'orange', 'black', 'sky', 'pink', 'lime', 'null']
    new_labels = []
    try:
        for label in labels:
            label_color = label_colors[random.randrange(11)]
            make_label_url = "https://api.trello.com/1/boards/%s/labels?name=%s&color=%s&key=%s&token=%s" \
                         % (board_id, label, label_color, key, token)
            response = requests.post(make_label_url)
            new_label = json.loads(response.text)
            new_labels.append(new_label['id'])
        return new_labels

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: could not add new labels")
        quit()


# This method takes in a board_id, a column name, the key and token and returns the column id
# If no column is found with that name, a new one will be created
# If board id, token or key are invalid an error message will print and the program will exit
def get_column_id(board_id, column_name, token, key):
    try:
        url = 'https://api.trello.com/1/boards/%s/lists/open?key=%s&token=%s' % (board_id, key, token)
        r = requests.get(url)
        board_lists = json.loads(r.text)
        for l in board_lists:
            if l['name'] == column_name:
                return l['id']

        return add_new_column(board_id, column_name, token, key)

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: could not retrieve columns")
        quit()


# This method takes in a board id, column name, token, and key, and adds new column to board
# If board_id, column_name, token, or key are invalid, error message will print and program will exit
def add_new_column(board_id, column_name, token, key):
    try:
        url = "https://api.trello.com/1/boards/%s/lists" % board_id
        querystring = {"name": column_name, "pos": "top", "key": key, "token": token}
        response = requests.request("POST", url, params=querystring)
        new_column = json.loads(response.text)
        return new_column['id']

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: Column could not be created")
        quit()


# This method takes in a column id, a card title, a list of label ids, a comment the token and the id
# It creates a card on the user's trello.com board
# If column id, comment, token or key are invalid an error message will print and it will exit
def add_new_card(column_id, card_title, label_id, comment, token, key):
    try:
        url = "https://api.trello.com/1/cards"
        querystring = {"name": card_title, "pos": "bottom", "idList": column_id, "idLabels": label_id,
                       "keepFromSource": "all", "key": key, "token": token}
        response = requests.request("POST", url, params=querystring)
        new_card = json.loads(response.text)
        add_comment(comment, new_card['id'], token, key)

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: card could not be added")
        quit()


# This method takes in a comment, card id, token and key and adds the comment to the users trello.com card
# If comment, card_id, token, or key are invalid it will print an error message and exit the program
def add_comment(comment, card_id, token, key):
    try:
        url = "https://api.trello.com/1/cards/%s/actions/comments" % card_id
        querystring = {"text": comment, "key": key, "token": token}
        response = requests.request("POST", url, params=querystring)
        json.loads(response.text)

    except (requests.RequestException, json.JSONDecodeError):
        print("Error: comment could not be added")
        quit()


if __name__ == "__main__":
    main(sys.argv[1:])
