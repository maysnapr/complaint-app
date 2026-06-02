ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login(username, password):
    return (
        username == ADMIN_USERNAME
        and
        password == ADMIN_PASSWORD
    )