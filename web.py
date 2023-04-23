from jnius import autoclass
from android.runnable import run_on_ui_thread


class WebViews:
    url = 'https://sims.nit.ac.tz/index.php/view_result'
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
