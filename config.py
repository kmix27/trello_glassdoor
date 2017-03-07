from trello import TrelloClient
import json


def configure(key, token, board_name):
    client = TrelloClient(api_key=key, token=token)
    new_board = client.add_board(board_name)
    for i in new_board.all_lists():
        i.close()
    links_label = new_board.add_label(name='Links', color='sky')
    desc_label = new_board.add_label(name='Description', color='purple')
    checklist_label = new_board.add_label(name='To Do', color='red')
    config = dict(board_id=new_board.id,
        link_l=links_label.id,
        desc_l=desc_label.id,
        check_l=checklist_label.id,
        key=key,
        token=token)
    with open('config.json', 'w') as c:
        json.dump(config, c)
        print('\nSuccessfully Created: config.json')
        print('Successfully Created: {}'.format(board_name))
        print('View board at: https://trello.com/b/{}\n'.format(config['board_id']))


def get_args():
    KEY = str(input('Your Trello API key:  '))
    TOKEN = str(input('Your Trello Token:  '))
    BOARD_NAME = str(input('Name your board:  '))
    return KEY, TOKEN, BOARD_NAME


def shell_cf():
    KEY, TOKEN, BOARD = get_args()
    configure(key=KEY, token=TOKEN, board_name=BOARD)


def main():
    try:
        shell_cf()
    except KeyboardInterrupt:
        print('\nCancelling...')


if __name__ == '__main__':
    main()
