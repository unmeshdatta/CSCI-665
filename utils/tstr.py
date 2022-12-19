

def convert(s):
    s = s.strip().lower()
    ind = 2 if not s[-2].isdigit() else 1
    lchar: str = s[-ind:]
    if not s[:-ind].isdigit():
        return False
    num = int(s[:-ind])
    if lchar.isdigit():
        return int(s)
    if 'y' == lchar:
        return num * 31536000
    elif 'mo' == lchar:
        return num * 2592000
    elif 'w' == lchar:
        return num * 604800
    elif 'd' == lchar:
        return num * 86400
    elif 'h' == lchar:
        return num * 3600
    elif 'm' == lchar:
        return num * 60
    elif 's' == lchar:
        return num
    else:
        return False
