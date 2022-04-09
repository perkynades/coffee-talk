from flexx import flx

class WebApp(flx.Widget):
    def init(self):
        flx.Label(text = 'Hello World!')

web_app = flx.App(WebApp)
web_app.export('index.html', link = 0)

web_app.launch('browser')
flx.run()
