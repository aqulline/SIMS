from jnius import autoclass
from android.runnable import run_on_ui_thread
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.base import EventLoop


class WebViews:
    url = ''
    webview = None

    @run_on_ui_thread
    def create_webview(self, **kwargs):
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        WebViews.webview = WebView(activity)
        WebViews.webview.getSettings().setJavaScriptEnabled(True)
        wvc = WebViewClient();
        WebViews.webview.setWebViewClient(wvc);
        activity.setContentView(WebViews.webview)
        WebViews.webview.loadUrl(WebViews.url)

        EventLoop.window.bind(on_keyboard=WebViews.on_key)
        Logger.info("WebView: opened {}".format(WebViews.url))

    @classmethod
    def on_back_button(self, *args):
        if WebViews.webview.canGoBack():
            WebViews.webview.goBack()
        else:
            # Unload the webview and go back to the previous screen
            WebViews.webview.loadUrl("about:blank")
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            import main
            app = main.MainApp()
            activity.setContentView(app)
            Window.unbind(on_keyboard=self.on_key)

    @classmethod
    def on_key(self, window, keycode, scancode, *args):
        print("hello")
        if keycode == 27:  # 27 is the keycode for the back button on Android
            self.on_back_button()
            return True  # indicate that the key event has been handled
        return False  # indicate that the key event has not been handled

    def start(cls, url):
        cls.url = url
        cls.create_webview()
        Logger.info("WebView: opened {}".format(cls.url))
