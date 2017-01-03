import shelve

def set_phones(phones):
    db = shelve.open('prefs')
    db['phones'] = phones
    db.close()

def get_phones():
    db = shelve.open('prefs')
    try:
        phones = db['phones']
    except KeyError:
        phones = []
    db.close()
    return phones
