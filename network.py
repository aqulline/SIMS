import requests


def ping_net():
    try:
        code = requests.get("https://www.google.com/search?q=google&oq=google&aqs=chrome..69i57j46i131i199i433i465i512j35i39i650l2j69i60j5j69i60l2.6577j0j7&sourceid=chrome&ie=UTF-8")

        print(code.status_code)

        if code.status_code == 200:
            return True

    except:
        return False

