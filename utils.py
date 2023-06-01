class Utils:
    user_name = "admin"
    database = "Dashboard"
    user_email = ""
    password = "password"
 
    def __init__(self):
        Utils.user_email = ""
    
    def is_float(str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    def is_tenth(str):
        if str.isdigit():
            return False
        try:
            float(str)
            dec_places = str.split(".")[-1]
            if len(dec_places) == 1:
                return True
            else:
                return False
        except:
            return False