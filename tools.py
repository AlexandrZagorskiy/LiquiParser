
def get_idtf(word):
    word = word.lower().replace(" ", "_")
    word = word.replace("-", "")
    word = word.replace("'", "")
    word = word.replace("?", "x")
    word = word.replace(" (standin)", "")    
    word = word.replace(" (inactive)", "")
    word = word.replace("(", "")
    word = word.replace(")", "")
    word = word.replace("&", "and")
    return word
    