def int_to_rank(num: int) -> str:

    num = int(num)

    if 10 <= num % 100 <= 20:
        return f'{num}th'
    elif num % 10 == 1:
        return f'{num}st'
    elif num % 10 == 2:
        return f'{num}nd'
    elif num % 10 == 3:
        return f'{num}rd'
    else:
        return f'{num}th'