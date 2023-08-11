import json

import requests
import time

from bs4 import BeautifulSoup
# from kivymd.toast import toast
# from kivymd.toast import toast
from plyer import notification


# URL of the login page

class NotifyResult:
    login_url = 'https://sims.nit.ac.tz/index.php/login/?callback=https://sims.nit.ac.tz/index.php'

    # URL of the page you want to monitor
    url = 'https://sims.nit.ac.tz/index.php/view_result'

    list_gpa = []
    list_cos = []
    list_remark = []
    list_gpa_offline = []
    list_cos_offline = []
    list_remark_offline = []
    size_of_table = []
    data_file_name = ""

    data_rslt = {}

    course_headers = ['Course Code', 'Course Name', 'Unit', 'CA', 'SE', 'Total', 'Grade', 'Point', 'Remark']

    def logged_in(self, session):
        responses = session.get(self.url)
        html = responses.content

        # print(html)

        # getting raw data
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.find_all('table', attrs={'class': 'table table-responsive table-bordered'})

        if name:
            print("Logged in successfully!")
            pass

            return True
        else:
            print("Not Logged in")

            return False

    def Session(self, name, password):
        # Credentials
        username = name
        password = password

        # Create a session
        session = requests.Session()

        # Authenticate
        login_data = {
            'identity': username,
            'password': password
        }
        response = session.post(self.login_url, data=login_data)

        if response.status_code == 200:
            if self.logged_in(session):
                print("Logged in successfully!")

                response = session.get(self.url)

                self.get_gpa(response.content)

                return True
            else:
                return False

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

    def get_gpa(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        bold = soup.find("div", id="cont")

        if bold.find_all("table"):

            for bl in bold.find_all("b"):
                if bl.text.__len__() >= 7:
                    self.cos_simpl(bl.text)
                else:
                    pass

            for i in range(bold.find_all("table").__len__()):
                x = bold.find_all("table")[i]

                z = x.find_all("tr")

                if len(z) >= 5:
                    s = x.find_all("tr")[len(z) - 1]
                    d = s.find_all("td")

                    data = d[1:]
                    NotifyResult.list_gpa.append(data[0].text)
                    NotifyResult.list_remark.append(data[1].text)

            for i in range(bold.find_all("table").__len__()):
                x = bold.find_all("table")[i]

                z = x.find_all("tr")
                if len(z) >= 5:
                    NotifyResult.size_of_table.append(len(z) - 2)
                    self.course_data.append(len(z) - 2)
                    for j in range(len(z) - 1):
                        s = x.find_all("tr")[j]
                        d = s.find_all("td")
                        for l in range(len(d) - 1):
                            course = {d[0].text.strip(): {
                                self.course_headers[o]: d[o].text.strip()
                                for o in range(self.course_headers.__len__())
                            }}
                            if course not in self.course_data:
                                self.course_data.append(course)

            self.save_offline()
            self.save_all_offline(self.to_organize(self.course_data, self.list_cos))
            self.course_data = []

    course_data = []

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
            time.sleep(.5)  # Wait for 1 minute before checking again

    def save_offline(self):
        self.data_file_name = "data/results.json"
        for i in range(self.list_cos.__len__()):
            data = {self.list_cos[i]: {"GPA": self.list_gpa[i], "Remark": self.list_remark[i]}}
            previous = self.load()
            if previous:
                if self.list_cos[i] not in previous:
                    all_data = {**data, **previous}
                    self.write(all_data)
            else:
                self.write(data)

    def save_all_offline(self, data):
        self.data_file_name = "data/all_results.json"
        previous = self.load()
        if previous:
            all_data = {**data, **previous}
            self.write(all_data)
        else:
            self.write(data)

    def load_offline(self):
        self.data_file_name = "data/results.json"
        data = self.load()

        for i, y in data.items():
            self.list_cos_offline.append(i)
            self.list_remark_offline.append(y["Remark"])
            self.list_gpa_offline.append(y["GPA"])

        return data

    def write(self, data):
        with open(self.data_file_name, "w") as file:
            initial_data = json.dumps(data, indent=4)
            file.write(initial_data)

    def load(self):
        with open(self.data_file_name, "r") as file:
            initial_data = json.load(file)
        return initial_data

    def cos_simpl(self, cos):
        s = cos.split()
        if len(s) > 7:
            p = len(s) - 7
            o = s[p:]
            l = " "
            m = l.join(o)
            NotifyResult.list_cos.append(m)

            return m

    def to_organize(self, total_data, list_cos):
        i = 0  # Index for iterating through the total_data list
        cote = 0
        organized_data = {}

        while i < len(total_data):
            count_or_course = total_data[i]
            i += 1

            if isinstance(count_or_course, int):  # If it's a count
                count = count_or_course
                courses = {}

                for _ in range(count):
                    course_dict = total_data[i]
                    print("dick", course_dict)
                    course_code = list(course_dict.keys())[0]
                    courses[course_code] = course_dict[course_code]
                    i += 1
                count = list_cos[cote]
                cote += 1
                organized_data[count] = courses
            else:  # If it's a single course
                course_code = list(count_or_course.keys())[0]
                organized_data[course_code] = count_or_course[course_code]

        return organized_data

# NotifyResult.Session(NotifyResult(), 'Nit/bcict/2020/458', 'MBUYA')
