from flet import Page, app, AppView
from units.workplace import Workplace


def main(page: Page):
    page.title = "Photo Editor App"
    page.padding = 0
    workplace = Workplace(None, page)
    page.add(workplace)
    page.update()

app(target=main)#, view=AppView.WEB_BROWSER)

# flet run app\node\main.py
# flet run main.py