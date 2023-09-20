import os
import re
import threading

from kivy.base import EventLoop
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, DictProperty
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy import utils
from kivymd.toast import toast
import json

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField

import network
from notify import NotifyResult as NS

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)


class Content(MDBoxLayout):
    gpa = StringProperty("")
    remark = StringProperty("")
    level_name = StringProperty("")


class Invoice(MDCard):
    name = StringProperty("")
    icon = StringProperty("cash-multiple")


class NumberOnlyField(MDTextField):
    pat = re.compile('[^0-9]')

    input_type = "number"

    def insert_text(self, substring, from_undo=False):

        pat = self.pat

        if "." in self.text:
            s = re.sub(pat, "", substring)

        else:
            s = ".".join([re.sub(pat, "", s) for s in substring.split(".", 1)])

        return super(NumberOnlyField, self).insert_text(s, from_undo=from_undo)


class MainApp(MDApp):
    # app
    size_x, size_y = Window.size
    added_widgets = []
    chips_color = ['CA', 'SE', 'Total', 'Grade', 'Remark']
    check = True

    # screens
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    # status
    status = StringProperty("")
    state = BooleanProperty(False)

    # files
    read = ""
    code_bool = False
    passcode = StringProperty("")

    # user
    user_id = StringProperty("")
    user_password = StringProperty("")

    # results data
    cos_code = StringProperty("")
    total = StringProperty("")
    unit = StringProperty("")
    grade = StringProperty("")
    ca = StringProperty("")
    point = StringProperty("")
    remark = StringProperty("")
    se = StringProperty("")

    def on_start(self):
        self.keyboard_hooker()

    def keyboard_hooker(self, *args):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        print(self.screens_size)
        if key == 27 and self.screens_size > 0:
            print(f"your were in {self.current}")
            last_screens = self.current
            self.screens.remove(last_screens)
            print(self.screens)
            self.screens_size = len(self.screens) - 1
            self.current = self.screens[len(self.screens) - 1]
            self.screen_capture(self.current)
            return True
        elif key == 27 and self.screens_size == 0:
            toast('Press Home button!')
            return True

    def pin_verify(self, id):
        code = self.root.ids.pin
        code1 = id.text
        lp = self.root.ids.l
        if code.text != code1:
            code.password = True
            id.password = True
            self.code_bool = False
            return True
        elif code.text == code1:
            id.error = False
            code.password = False
            id.password = False
            self.code_bool = True
            lp.pos_hint = {'center_x': .65, 'center_y': .45}
            return False

    def pin_save(self):
        if self.code_bool:
            code = self.root.ids.pin
            self.passcode = code.text
            with open("register.txt", "w") as fl:
                fl.write(self.passcode)
            fl.close()
            sm = self.root
            sm.current = "login_view"

        if not self.code_bool:
            toast("Pin not Match!")

    def pin_check(self):
        file_size = os.path.getsize("register.txt")
        if file_size == 0:
            sm = self.root
            sm.current = "register_code"
        else:
            sm = self.root
            sm.current = "login_view"

    def login_view(self):
        with open("register.txt", "r") as fl:
            read = fl.readlines()
            self.read = read[0]
            cd = self.root.ids.login_code
            lk = self.root.ids.locks
            lg = self.root.ids.view
            if cd.text == self.read:
                toast("Succes!")
                cd.password = False
                lk.icon = "lock-open-variant"
                lg.pos_hint = {'center_x': .65, 'center_y': .45}
            else:
                cd.password = True
                lk.icon = "lock"
                lg.pos_hint = {'center_x': .65, 'center_y': 2}

    def login_verify(self, reg, password):
        if reg != "" and password != "":
            if self.state:
                if NS.Session(NS(), reg, password):
                    self.register_user(reg, password)
                else:
                    print("Not")
            else:
                self.snack_bar()
        else:
            toast("Fill required space!")

    def register_user(self, name, code):
        with open("user.json", "w") as file:
            data = {"reg": name, "password": code}
            data_dump = json.dumps(data, indent=6)
            file.write(data_dump)
            file.close()
            self.pin_check()

    def login_check(self):
        file_size = os.path.getsize("user.json")
        file_code = os.path.getsize("register.txt")
        if file_size == 0:
            sm = self.root
            sm.current = "login"
        else:
            data = self.load("user.json")
            self.user_id, self.user_password = data["reg"], data["password"]
            if self.state:
                NS.Session(NS(), self.user_id, self.user_password)
            if file_code != 0:
                sm = self.root
                sm.current = "login_view"
            else:
                sm = self.root
                sm.current = "register_code"

    def offline_results(self):
        NS.load_offline(NS())
        if NS.list_gpa_offline.__len__() > 0:
            for i in range(NS.list_gpa_offline.__len__()):
                Content.gpa = str(NS.list_gpa_offline[i])
                Content.remark = str(NS.list_remark_offline[i])
                Content.level_name = str(NS.list_cos_offline[i])
                Panel = MDExpansionPanel(
                    icon="book-multiple-outline",
                    content=Content(),
                    panel_cls=MDExpansionPanelTwoLine(
                        text=str(NS.list_cos_offline[i].split("-")[0].replace("::", "")),
                        secondary_text=NS.list_cos_offline[i].split("-")[1],
                    )
                )
                self.root.ids.box.add_widget(Panel)
                self.added_widgets.append(Panel)
            print(self.added_widgets)
        else:
            Label = MDLabel(text="No Results", halign="center")
            self.root.ids.box.add_widget(Label)

    def offline_invo(self):
        NS.load_inv_offline(NS())
        if NS.invoice_year.__len__() > 0:
            for i in range(NS.invoice_year.__len__()):
                Invoice.name = NS.invoice_year[i]
                Panel = Invoice(name=NS.invoice_year[i])
                self.root.ids.boxInvo.add_widget(Panel)
                self.added_widgets.append(Panel)
            print(self.added_widgets)
        else:
            Label = MDLabel(text="No Invo", halign="center")
            self.root.ids.box.add_widget(Label)

    def get_invoice_data(self, year):
        data_list = NS.get_year_data(NS(), year)
        self.display_invoice(data_list)

    year_holder = StringProperty("")
    def display_invoice(self, data):
        self.root.ids.invoices.data = {}
        for i in data:
            for x, y in i.items():
                self.root.ids.invoices.data.append(
                    {
                        "viewclass": "Invoices",
                        "number": y["nvoiceNo"],
                        "control": y["Control Number"],
                        "invoice_amount": y["Invoice"],
                        "paid": y["Amount"],
                        "balance": y["Paid"],
                        "head": y["Description"]
                    }
                )

    def get_cos_name(self, name):
        self.root.ids.cos.text = name

    def add_ddt(self):
        if self.check:
            self.clear_widgets()
            if network.ping_net():
                NS.Session(NS(), self.user_id, self.user_password)
                self.offline_results()
                print("net work")
            else:
                self.offline_results()
            self.check = False

    def clear_widgets(self):
        map = self.root.ids.box
        for widget in self.added_widgets:
            print(widget.icon)
            map.remove_widget(widget)
        self.added_widgets = []

    def refresh(self):
        if self.state:
            NS.Session(NS(), self.user_id, self.user_password)
            self.add_ddt()

    def get_all_result(self, name):
        data = self.load("data/all_results.json")
        print(data[name])
        self.data = data[name]
        self.display_result(data[name])

    units = StringProperty("Grade")

    def display_result(self, name):
        self.root.ids.result.data = {}
        for i in name.keys():
            self.root.ids.result.data.append(
                {
                    "viewclass": "ResultCard",
                    "name": name[i]["Course Name"],
                    "grade": name[i][self.units],
                    "id": i
                }
            )

    def update_color(self, name):
        re = self.root.ids.results
        for child in re.children:
            if child.ids:
                for _ in self.chips_color:
                    if child.text == name.text:
                        child.color = 180 / 255, 146 / 255, 255 / 255, 1
                    else:
                        child.color = 36 / 255, 146 / 255, 255 / 255, 1

    def update_units(self):
        self.root.ids.result.data = {}
        for i in self.data.keys():
            if "/" in self.data[i][self.units]:
                self.data[i][self.units] = self.data[i][self.units].strip().split("/")[0]
            elif self.units == "Total":
                self.data[i][self.units] = f"{self.data[i][self.units]}"
            self.root.ids.result.data.append(
                {
                    "viewclass": "ResultCard",
                    "name": self.data[i]["Course Name"],
                    "grade": self.data[i][self.units],
                    "id": i
                }
            )

    data = DictProperty({})

    def snack_bar(self):
        snackbar = Snackbar(
            text="Check the Sims status first!",
            bg_color=(26 / 255, 54 / 255, 113 / 255, 1),
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        snackbar.size_hint_x = (
                                       Window.width - (snackbar.snackbar_x * 2)
                               ) / Window.width
        snackbar.buttons = [
            MDRaisedButton(
                text="Check",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                on_release=lambda x: self.screen_capture("check")
            )
        ]
        snackbar.open()

    def display_results(self, name):
        data = self.data
        self.cos_code = data[name]['Course Code']
        self.total = data[name]['Total']
        self.unit = data[name]['Unit']
        self.grade = data[name]['Grade']
        self.ca = data[name]['CA']
        self.point = data[name]['Point']
        self.remark = data[name]['Remark']
        self.se = data[name]['SE']

    def run_sims(self):

        if self.state:
            print(self.state)
            from web import WebViews as WV
            WV.url = 'https://sims.nit.ac.tz/index.php/dashboard'
            Clock.schedule_once(WV.create_webview, 0)
        else:
            toast("check the Sims status first")

    def run_results(self):

        if self.state:
            from web import WebViews as WV
            WV.url = 'https://sims.nit.ac.tz/index.php/view_result'
            Clock.schedule_once(WV.create_webview, 0)
        else:
            toast("check the Sims status first")

    def run_create_invoice(self):

        if self.state:
            from web import WebViews as WV
            WV.url = 'https://sims.nit.ac.tz/index.php/create_invoice'
            Clock.schedule_once(WV.create_webview, 0)
        else:
            toast("check the Sims status first")

    def run_invoice(self):
        if self.state:
            from web import WebViews as WV
            WV.url = 'https://sims.nit.ac.tz/index.php/invoice_list'
            Clock.schedule_once(WV.create_webview, 0)
        else:
            toast("check the Sims status first")

    def wait_ping(self):
        toast("Wait a moment!")
        Clock.schedule_once(self.ping_sims, .1)

    def ping_sims(self, *kwargs):
        import requests
        try:
            code = requests.get("https://sims.nit.ac.tz/index.php/view_result")
            print(code.status_code)
            if code.status_code == 200:
                self.status = "Available"
                icon = self.root.ids.status_icon
                leash = self.root.ids.back_leash
                icon.icon = "wifi"
                icon.text_color = 0, 1, 0, .7
                leash.md_bg_color = 0, 1, 0, .7

                self.state = True

                thread = threading.Thread(target=NS.Get_data, args=(NS(),))
                thread.start()

            else:
                self.status = "Not Available"
                icon = self.root.ids.status_icon
                leash = self.root.ids.back_leash
                icon.icon = "wifi"
                icon.text_color = 1, 0, 0, .7

                leash.md_bg_color = 1, 0, 0, .7

        except:
            toast("network problem!")
            self.status = "network problem!"
            icon = self.root.ids.status_icon
            leash = self.root.ids.back_leash
            sts = self.root.ids.status
            icon.icon = "wifi"
            icon.text_color = 1, 0, 0, .7
            sts.text_color = 1, 0, 0, .7

            leash.md_bg_color = 1, 0, 0, .7

    def load(self, data_file_name):
        with open(data_file_name, "r") as file:
            initial_data = json.load(file)
        return initial_data

    def toast_this(self, name):
        toast(name)

    def screen_capture(self, screen):
        sm = self.root
        sm.current = screen
        if screen in self.screens:
            pass
        else:
            self.screens.append(screen)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        print(f'size {self.screens_size}')
        print(f'current screen {screen}')

    def screen_leave(self):
        print(f"your were in {self.current}")
        last_screens = self.current
        self.screens.remove(last_screens)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        self.screen_capture(self.current)

    def build(self):
        pass


MainApp().run()
