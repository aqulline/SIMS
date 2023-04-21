from jnius import autoclass
from jnius import cast
from android.runnable import run_on_ui_thread
from kivy.clock import Clock


class WebView:
    url = "https://sims.nit.ac.tz/index.php/view_result"
    webview = None

    @run_on_ui_thread
    def create_webview(self, **kwargs):
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        WebView.webview = WebView(activity)
        WebView.webview.getSettings().setJavaScriptEnabled(True)
        wvc = WebViewClient();
        WebView.webview.setWebViewClient(wvc);
        activity.setContentView(WebView.webview)
        WebView.webview.loadUrl(WebView.url)
