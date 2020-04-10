

def get_discrete_representation_for_word(keyboard, word):
    """
    Returns list of key_ids that would be included in the perfect swype for this word
    e.g. in the standard T9 layout 'hello' --> [3, 2, 4, 6]
    Parameters
    ----------
    keyboard: nuvox.keyboard.Keyboard
    word: str

    Returns
    -------
    discrete_repr: list[str]

    Raises
    -------
    ValueError
        if word contains a char that doesn't exist in keyboard
    """
    discrete_repr = []
    for char in list(word):
        key = keyboard.char_to_key[char]
        if (not discrete_repr) or (discrete_repr and key.key_id != discrete_repr[-1]):
            discrete_repr.append(key.key_id)

    return discrete_repr

