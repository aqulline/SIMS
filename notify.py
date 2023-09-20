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
    inv = 'https://sims.nit.ac.tz/index.php/invoice_list'

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
        responses = session.get(self.inv)
        html = responses.content

        # print(html)

        # getting raw data
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.find('div', attrs={'class': 'ibox-content clearfix'})

        if name:
            return True
        else:
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

                inv_response = session.get(self.inv)
                self.get_invoice(inv_response.content)

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

        if bold:
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

    def get_invoice(self, content):

        hd = ["S/No", "Pick", "nvoiceNo", "Control Number", "Description", "Payment Mode", "Currency", "Invoice",
              "Amount",
              "Paid", "Amount", "Balance", "Statement"]

        html = content

        # getting raw data
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.find('div', attrs={'class': 'ibox-content clearfix'})

        headd = soup.find_all('div', attrs={
            'style': 'font-weight: bold; color: brown; font-size: 15px; border-bottom: 1px solid brown; margin-bottom: 10px;'})

        tbl = name.find_all("table")

        data_main = {}
        for i in range(tbl.__len__() - 1):
            tr = tbl[i].find_all("tr")
            print(headd[i].text)
            head = headd[i].text
            for j in range(tr.__len__()):
                td = tr[j].find_all("td")
                if td:
                    for k in range(td.__len__() - 1):
                        # print(hd[k], td[k].text)
                        data = {f"{td[0].text}_{head}": {td[0].text: {
                            hd[p]: td[p].text
                            for p in range(td.__len__() - 1)}}}

                        data_main = {**data_main, **data}

                        print(data)
                        """data_temp = {headd[i].text: {td[0].text for o in range(): {
                            hd[o]: td[o].text
                            for o in range(td.__len__() - 1)}}}
                        data_main = {**data_temp, **data_main}"""
        print(data_main)
        self.save_offline_inv(data_main)

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

    def save_offline_inv(self, data):
        self.data_file_name = "data/invoice.json"
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

    invoice_year = []

    def get_invoice_year(self, data):

        return data.strip().split(":")[1]

    def load_inv_offline(self):
        self.data_file_name = "data/invoice.json"
        data = self.load()
        for i, y in data.items():
            year = self.get_invoice_year(i)

            if year.strip() not in self.invoice_year:
                self.invoice_year.append(year.strip())

    def get_year_data(self, years):
        self.data_file_name = "data/invoice.json"
        data = self.load()
        years_list = []
        for x, z in data.items():
            if years == self.get_invoice_year(x).strip():
                print(data[x])

                years_list.append(data[x])

        return years_list

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
