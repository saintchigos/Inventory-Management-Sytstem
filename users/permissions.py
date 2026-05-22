def is_storesman(user):
    return user.role == 'storesman'


def is_procurement(user):
    return user.role == 'procurement'


def is_accounts(user):
    return user.role == 'accounts'


def is_principal(user):
    return user.role == 'principal'


def is_it(user):
    return user.role == 'it'