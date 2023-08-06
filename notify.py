import requests
import time

from bs4 import BeautifulSoup
from plyer import notification


# URL of the login page

class NotifyResult:
    login_url = 'https://sims.nit.ac.tz/index.php/login/?callback=https://sims.nit.ac.tz/index.php'

    # URL of the page you want to monitor
    url = 'https://sims.nit.ac.tz/index.php/view_result'

    def change(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find("div", class_="wrapper wrapper-content animated fadeInRight")

        # print(table)
        import hashlib

        # Assume previous_html is the hash of the previous version of the HTML content

        # Get the current HTML content
        current_htm = str(table)

        # print(current_htm)
        # Create an SHA-256 hash object for the current HTML content
        hash_object = hashlib.sha256()
        hash_object.update(current_htm.encode('utf-8'))
        current_hash = hash_object.hexdigest()

        print("Current Hash:", current_hash)

        return current_hash



    def Get_data(self):
        # Credentials
        username = 'Nit/bcict/2020/458'
        password = 'MBUYA'

        # Create a session
        session = requests.Session()

        # Authenticate
        login_data = {
            'identity': username,
            'password': password
        }
        response = session.post(self.login_url, data=login_data)

        if response.status_code == 200:
            print("Logged in successfully!")

        # Monitor changes
        previous_hash = '9306da3a2ddbabc6e3b422328b030e26c6376fe9be3299039ef3d0bae23cd00b'
        count = 0
        while True:
            try:
                response = session.get(self.url)
                import hashlib

                self.change(response.content)
                if count == 2:
                    current_hash = self.change(response.content)
                    notification.notify(
                        title="Result",
                        message="You will be notified when results comes out",
                        timeout=10,
                        app_icon="components/icons/sim.png"
                    )

                    # Compare the hashes
                    if current_hash != previous_hash:
                        print("Website content has changed!")

                        notification.notify(
                            title="Result",
                            message="Changes in SIMS",
                            timeout=10,
                            app_icon="components/icons/sim.png"
                        )

                        # Do something here, like sending a notification

                    # Update the previous_hash for the next iteration
                    previous_hash = current_hash

                    return False
                else:
                    count += 1

            except requests.RequestException as e:
                print("Error:", e)

            # Adjust the time interval based on your needs
            time.sleep(6)  # Wait for 1 minute before checking again


