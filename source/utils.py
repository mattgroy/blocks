def count_score(num):
    if num is not None:
        num = int(num)
        if 2 < num:
            return num * num
        elif num == 2:
            return 2
        else:
            return 0
    return 0
