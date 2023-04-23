from kivy.base import EventLoop
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy import utils
from kivymd.toast import toast

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)


# https://sims.nit.ac.tz/index.php/view_result


class MainApp(MDApp):
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    size_x, size_y = Window.size

    status = StringProperty("")
    state = BooleanProperty(False)

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

    def build(self):
        pass

    def run_sims(self):

        if self.state:
            from web import WebViews as WV
            Clock.schedule_once(WV.create_webview, 0)
        else:
            toast("check the Sims status first")

    def ping_sims(self):
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


MainApp().run()
