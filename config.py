from trello import TrelloClient
import json
import argparse


def main(key, token, board_name):
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
        print('\nSuccessfully Created: {}'.format(board_name))
        print('\nView board at: https://trello.com/b/{}\n'.format(config['board_id']))


parser = argparse.ArgumentParser()
parser.add_argument('key', type=str, help='add your trello api key')
parser.add_argument('token', type=str, help='add your trello api token')
parser.add_argument('board_name', type=str, help='what you would like to name your board')
args = parser.parse_args()

main(key=args.key, token=args.token, board_name=args.board_name)
