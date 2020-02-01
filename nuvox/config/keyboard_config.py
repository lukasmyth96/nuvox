required_key_attributes = ['x1', 'y1', 'w', 'h', 'key_id', 'contents', 'type']

nuvox_standard_keyboard = [
    {'x1': 0/3, 'y1': 0, 'w': 2/3, 'h': 1/5, 'key_id': 'display_frame', 'contents': [], 'type': 'display_frame'},
    {'x1': 6/9, 'y1': 0, 'w': 1/3, 'h': 1/10, 'key_id': 'speak_button', 'contents': ['speak'], 'type': 'speak_button'},
    {'x1': 6/9, 'y1': 1/10, 'w': 1/9, 'h': 1/10, 'key_id': 'enter_button', 'contents': ['del'], 'type': 'delete_button'},
    {'x1': 7/9, 'y1': 1/10, 'w': 1/9, 'h': 1/10, 'key_id': 'clear_button', 'contents': ['clear'], 'type': 'clear_button'},
    {'x1': 8/9, 'y1': 1/10, 'w': 1/9, 'h': 1/10, 'key_id': 'exit_button', 'contents': ['X'], 'type': 'exit_button'},
    {'x1': 0/3, 'y1': 1/5, 'w': 1/3, 'h': 1/5, 'key_id': '1', 'contents': ['a', 'b', 'c'], 'type': 'button'},
    {'x1': 1/3, 'y1': 1/5, 'w': 1/3, 'h': 1/5, 'key_id': '2', 'contents': ['d', 'e', 'f'], 'type': 'button'},
    {'x1': 2/3, 'y1': 1/5, 'w': 1/3, 'h': 1/5, 'key_id': '3', 'contents': ['g', 'h', 'i'], 'type': 'button'},
    {'x1': 0/3, 'y1': 2/5, 'w': 1/3, 'h': 1/5, 'key_id': '4', 'contents': ['j', 'k', 'l'], 'type': 'button'},
    {'x1': 1/3, 'y1': 2/5, 'w': 1/3, 'h': 1/5, 'key_id': '5', 'contents': [' '], 'type': 'button'},
    {'x1': 2/3, 'y1': 2/5, 'w': 1/3, 'h': 1/5, 'key_id': '6', 'contents': ['m', 'n', 'o'], 'type': 'button'},
    {'x1': 0/3, 'y1': 3/5, 'w': 1/3, 'h': 1/5, 'key_id': '7', 'contents': ['p', 'q', 'r', 's'], 'type': 'button'},
    {'x1': 1/3, 'y1': 3/5, 'w': 1/3, 'h': 1/5, 'key_id': '8', 'contents': ['t', 'u', 'v'], 'type': 'button'},
    {'x1': 2/3, 'y1': 3/5, 'w': 1/3, 'h': 1/5, 'key_id': '9', 'contents': ['w', 'x', 'y', 'z'], 'type': 'button'},
    {'x1': 0/3, 'y1': 4/5, 'w': 1/3, 'h': 1/5, 'key_id': '10', 'contents': [','], 'type': 'button'},
    {'x1': 1/3, 'y1': 4/5, 'w': 1/3, 'h': 1/5, 'key_id': '11', 'contents': ['.'], 'type': 'button'},
    {'x1': 2/3, 'y1': 4/5, 'w': 1/3, 'h': 1/5, 'key_id': '12', 'contents': ['?'], 'type': 'button'},
]

nuvox_qwerty_keyboard = [
    {'x1': 0/10, 'y1': 0/5, 'w': 7/10, 'h': 1/5, 'key_id': 'display_bar', 'contents': [], 'type': 'display'},
    {'x1': 7/10, 'y1': 0/5, 'w': 2/10, 'h': 1/5, 'key_id': 'enter_button', 'contents': ['del'], 'type': 'delete_button'},
    {'x1': 9/10, 'y1': 0/5, 'w': 1/10, 'h': 1/5, 'key_id': 'enter_button', 'contents': ['X'], 'type': 'exit_button'},
    {'x1': 0/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'q', 'contents': ['q'], 'type': 'button'},
    {'x1': 1/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'w', 'contents': ['w'], 'type': 'button'},
    {'x1': 2/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'e', 'contents': ['e'], 'type': 'button'},
    {'x1': 3/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'r', 'contents': ['r'], 'type': 'button'},
    {'x1': 4/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 't', 'contents': ['t'], 'type': 'button'},
    {'x1': 5/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'y', 'contents': ['y'], 'type': 'button'},
    {'x1': 6/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'u', 'contents': ['u'], 'type': 'button'},
    {'x1': 7/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'i', 'contents': ['i'], 'type': 'button'},
    {'x1': 8/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'o', 'contents': ['o'], 'type': 'button'},
    {'x1': 9/10, 'y1': 1/5, 'w': 1/10, 'h': 1/5, 'key_id': 'p', 'contents': ['p'], 'type': 'button'},
    {'x1': 1/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'a', 'contents': ['a'], 'type': 'button'},
    {'x1': 3/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 's', 'contents': ['s'], 'type': 'button'},
    {'x1': 5/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'd', 'contents': ['d'], 'type': 'button'},
    {'x1': 7/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'f', 'contents': ['f'], 'type': 'button'},
    {'x1': 9/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'g', 'contents': ['g'], 'type': 'button'},
    {'x1': 11/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'h', 'contents': ['h'], 'type': 'button'},
    {'x1': 13/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'j', 'contents': ['j'], 'type': 'button'},
    {'x1': 15/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'k', 'contents': ['k'], 'type': 'button'},
    {'x1': 17/20, 'y1': 2/5, 'w': 1/10, 'h': 1/5, 'key_id': 'l', 'contents': ['l'], 'type': 'button'},
    {'x1': 0/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': '.', 'contents': ['.'], 'type': 'button'},
    {'x1': 1/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'z', 'contents': ['z'], 'type': 'button'},
    {'x1': 2/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'x', 'contents': ['x'], 'type': 'button'},
    {'x1': 3/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'c', 'contents': ['c'], 'type': 'button'},
    {'x1': 4/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'v', 'contents': ['v'], 'type': 'button'},
    {'x1': 5/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'b', 'contents': ['b'], 'type': 'button'},
    {'x1': 6/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'n', 'contents': ['n'], 'type': 'button'},
    {'x1': 7/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': 'm', 'contents': ['m'], 'type': 'button'},
    {'x1': 8/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': ',', 'contents': [','], 'type': 'button'},
    {'x1': 9/10, 'y1': 3/5, 'w': 1/10, 'h': 1/5, 'key_id': '?', 'contents': ['?'], 'type': 'button'},
    {'x1': 0/10, 'y1': 4/5, 'w': 3/10, 'h': 1/5, 'key_id': '<clear>', 'contents': ['clear'], 'type': 'clear_button'},
    {'x1': 3/10, 'y1': 4/5, 'w': 4/10, 'h': 1/5, 'key_id': '<space>', 'contents': [' '], 'type': 'button'},
    {'x1': 7/10, 'y1': 4/5, 'w': 3/10, 'h': 1/5, 'key_id': '<speak>', 'contents': ['speak'], 'type': 'speak_button'},
]