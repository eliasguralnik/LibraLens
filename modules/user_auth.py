from server import database


def auth_process(auth):
    print(auth)
    type_status, data = auth_type(auth)
    if type_status is True:
        status, existing_user = user_auth_log(data)
        return status, existing_user
    elif type_status is False:
        status, existing_user = user_auth_reg(data)
        return status, existing_user
    else:
        print("error")
        return None, None


def auth_type(auth):
    try:
        if "registration" in auth:
            auth_lst = auth.split(' ', 1)
            reg_data = auth_lst[1]
            print(reg_data)
            return False, reg_data
        elif "login" in auth:
            auth_lst = auth.split(' ', 1)
            log_data = auth_lst[1]
            print(log_data)
            return True, log_data

    except Exception as e:
        print(e)


def user_auth_reg(user_data):
    print("register", user_data)
    user, password = user_data.split()
    print(user)
    print(password)
    status, existing_user = database.write_reg_data(user, password)
    print(status, existing_user)
    return status, existing_user


def user_auth_log(user_data):
    print("login", user_data)
    user, password = user_data.split()
    print(user)
    print(password)
    status, existing_user = database.check_log_data(user, password)
    print(status, existing_user)
    return status, existing_user


if __name__ == '__main__':
    auth = "login elias 555"
    xxx = auth_process(auth)
    print(xxx[1][1])
