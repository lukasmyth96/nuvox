from nuvox.key import Key

nuvox_standard_keyboard = [Key(x1=0/8, y1=0/8, w=7/8, h=1/8, key_id='display', contents=[], widget_type='text'),
                           Key(x1=7/8, y1=0/8, w=1/8, h=1/8, key_id='exit', contents=['X']),

                           Key(x1=0/8, y1=1/8, w=1/8, h=1/8, key_id='suggestion_left_arrow', contents=['←']),
                           Key(x1=1/8, y1=1/8, w=2/8, h=1/8, key_id='suggestion_1', contents=['']),
                           Key(x1=3/8, y1=1/8, w=2/8, h=1/8, key_id='suggestion_2', contents=['']),
                           Key(x1=5/8, y1=1/8, w=2/8, h=1/8, key_id='suggestion_3', contents=['']),
                           Key(x1=7/8, y1=1/8, w=1/8, h=1/8, key_id='suggestion_right_arrow', contents=['→']),

                           Key(x1=0/8, y1=1/4, w=1/8, h=1/4, key_id='number_switch', contents=['123']),
                           Key(x1=1/8, y1=1/4, w=2/8, h=1/4, key_id='1', contents=['a', 'b', 'c']),
                           Key(x1=3/8, y1=1/4, w=2/8, h=1/4, key_id='2', contents=['d', 'e', 'f']),
                           Key(x1=5/8, y1=1/4, w=2/8, h=1/4, key_id='3', contents=['g', 'h', 'i']),
                           Key(x1=7/8, y1=1/4, w=1/8, h=1/4, key_id='speak', contents=['speak']),

                           Key(x1=0/8, y1=2/4, w=1/8, h=1/4, key_id='text_switch', contents=['a|b|c']),
                           Key(x1=1/8, y1=2/4, w=2/8, h=1/4, key_id='4', contents=['j', 'k', 'l']),
                           Key(x1=3/8, y1=2/4, w=2/8, h=1/4, key_id='5', contents=['']),
                           Key(x1=5/8, y1=2/4, w=2/8, h=1/4, key_id='6', contents=['m', 'n', 'o']),
                           Key(x1=7/8, y1=2/4, w=1/8, h=1/4, key_id='delete', contents=['del']),

                           Key(x1=0/8, y1=3/4, w=1/8, h=1/4, key_id='settings_switch', contents=['⚙']),
                           Key(x1=1/8, y1=3/4, w=2/8, h=1/4, key_id='7', contents=['p', 'q', 'r', 's']),
                           Key(x1=3/8, y1=3/4, w=2/8, h=1/4, key_id='8', contents=['t', 'u', 'v']),
                           Key(x1=5/8, y1=3/4, w=2/8, h=1/4, key_id='9', contents=['w', 'x', 'y', 'z']),
                           Key(x1=7/8, y1=3/4, w=1/8, h=1/4, key_id='clear', contents=['clr'])]