from __future__ import annotations

import _thread
import json
import os
import time
from pathlib import Path

from importlib_metadata import version
from rich import box
from rich.console import RenderableType
from rich.json import JSON
from rich.markdown import Markdown
from rich.markup import escape
from rich.pretty import Pretty
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    RichLog,
    Static,
    Switch,
)

from ..__init__ import __version__
from ..System import testAll

from_markup = Text.from_markup

WELCOME_MD = """

## MocoBot

**欢迎使用MocoBot!** MocoBot是一个官方QQ机器人的SDK.
"""

RICH_MD = """

MocoBot 使用了 **Textual** 和 **Rich**, 非常漂亮的终端输出库(可爱才是第一生产力!).
为了正确且美观的输出，请Windows用户使用新版本命令行(wt)
也就是说这个项目是支持Rich库的 *renderables* 类型的 (这个文档就是用Rich的Markdown类生成的).

PS:这个项目允许你使用鼠标的(((

举几个例子:
"""

DATA = {
    "test": [
        1234,
        (
            "Moco",
            [],
            {1, 2},
            "Friend",
        ),
    ],
}

SETUP_MD = """

MocoBot需要您的一些信息才可以开始使用

请从q.qq.com(QQ开放平台)里面的机器人**开发设置**中找到对应信息输入下表

- **appId** 机器人ID,在API和事件监听中都要使用.
- **token** 机器人令牌,在事件监听里要用.
- **appSecret** 机器人密钥,在API鉴权Token申请中要用.
"""

MESSAGE = """
希望你能喜欢MocoBot!
以下是可能对你有用的链接

[@click="app.open_link('https://textual.textualize.io')"]MocoBot[/]

特别感谢
[@click="app.open_link('https://github.com/Textualize/textual')"]Textual[/]
[@click="app.open_link('https://github.com/Textualize/rich')"]Rich[/]


"""

JSON_EXAMPLE = """{
  "person": {
    "name": "Moco",
    "age": "18",
    "sex": "female",
    "hometown": {
      "province": "**省",
      "city": "**市",
      "county": "**县"
    },
    "friends":[
      "Friend1","Friend2","Friend3","Friend4"
    ]
  }
}
"""

VERSION = __version__


def try_login(appid: int, token: str, appSecret: str, self):
    if testAll(appid, appSecret):
        self.notify("[green]验证成功")
        self.app.add_note("[green]Login OK")
        data = {
            "appId": appid,
            "token": token,
            "appSecret": appSecret,
            "TUI": True
        }
        f = open("config.json", mode="w")
        json.dump(data, f)
        f.close()
        self.notify("完成设置，程序将在10s后退出")
        time.sleep(10)
        self.app.exit()

    else:
        self.query_one(Button).disabled = False
        self.notify("[red]信息错误!\n请检查输入的信息是否正确")
        self.app.add_note("[red]Login Error")


class Body(ScrollableContainer):
    pass


class Title(Static):
    pass


class DarkSwitch(Horizontal):
    def compose(self) -> ComposeResult:
        yield Switch(value=self.app.dark)
        yield Static("深色模式", classes="label")

    def on_mount(self) -> None:
        self.watch(self.app, "dark", self.on_dark_change, init=False)

    def on_dark_change(self) -> None:
        self.query_one(Switch).value = self.app.dark

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.app.dark = event.value


class Welcome(Container):
    def compose(self) -> ComposeResult:
        yield Static(Markdown(WELCOME_MD))
        yield Button("Start", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.add_note("[b magenta]Start!")
        self.app.query_one(".location-first").scroll_visible(duration=0.5, top=True)


class OptionGroup(Container):
    pass


class SectionTitle(Static):
    pass


class Message(Static):
    pass


class Version(Static):
    def render(self) -> RenderableType:
        return f"[b]v{VERSION}"


class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Title("MocoBot")
        yield OptionGroup(Message(MESSAGE), Version())
        yield DarkSwitch()


class AboveFold(Container):
    pass


class Section(Container):
    pass


class Column(Container):
    pass


class TextContent(Static):
    pass


class QuickAccess(Container):
    pass


class LocationLink(Static):
    def __init__(self, label: str, reveal: str) -> None:
        super().__init__(label)
        self.reveal = reveal

    def on_click(self) -> None:
        self.app.query_one(self.reveal).scroll_visible(top=True, duration=0.5)
        # self.app.add_note(f"Scrolling to [b]{self.reveal}[/b]")


class LoginForm(Container):
    def compose(self) -> ComposeResult:
        yield Static("appId", classes="label")
        yield Input(placeholder="appId", classes="appIdInput")
        yield Static("token", classes="label")
        yield Input(placeholder="token", classes="tokenInput")
        yield Static("appSecret", classes="label")
        yield Input(placeholder="appSecret", classes="appSecretInput")
        yield Static()
        yield Button("Login", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        try:
            appId = int(self.app.query_one(".appIdInput").value)
        except:
            self.notify("[red]机器人ID必须为数字")
            return
        if self.app.query_one(".tokenInput").value:
            token = self.app.query_one(".tokenInput").value
        else:
            self.notify("[red]token不能为空")
            return
        if self.app.query_one(".appSecretInput").value:
            self.app.add_note("[b magenta]Login")
            self.app.add_note(f'appId : {self.app.query_one(".appIdInput").value}\n'
                              f'token : {self.app.query_one(".tokenInput").value}\n'
                              f'appSecret : {self.app.query_one(".appSecretInput").value}')
            self.notify("尝试登陆...")
            self.query_one(Button).disabled = True
            _thread.start_new_thread(try_login,(int(self.app.query_one(".appIdInput").value), self.app.query_one(".tokenInput").value,
                      self.app.query_one(".appSecretInput").value, self))
        else:
            self.notify("[red]appSecret不能为空")
            return


class Window(Container):
    pass


class SubTitle(Static):
    pass


class SetupApp(App[None]):
    CSS_PATH = "setup.tcss"
    TITLE = "初始化MocoBot"
    BINDINGS = [
        ("ctrl+b", "toggle_sidebar", "侧边栏"),
        ("ctrl+t", "app.toggle_dark", "主题切换"),
        # ("ctrl+s", "app.screenshot()", "截屏"),
        ("f1", "app.toggle_class('RichLog', '-hidden')", "日志"),
        Binding("ctrl+q", "app.quit", "退出", show=True),
    ]

    show_sidebar = reactive(False)

    def add_note(self, renderable: RenderableType) -> None:
        self.query_one(RichLog).write(renderable)

    def compose(self) -> ComposeResult:
        example_css = Path(self.css_path[0]).read_text()
        yield Container(
            Sidebar(classes="-hidden"),
            Header(show_clock=False),
            RichLog(classes="-hidden", wrap=False, highlight=True, markup=True),
            Body(
                QuickAccess(
                    LocationLink("欢迎", ".location-top"),
                    LocationLink("Why MocoBot", ".location-mocoBot"),
                    LocationLink("配置", ".location-setup"),
                    # LocationLink("CSS", ".location-css"),
                ),
                AboveFold(Welcome(), classes="location-top"),
                Column(
                    Section(
                        SectionTitle("Why MocoBot"),
                        TextContent(Markdown(RICH_MD)),
                        SubTitle("Pretty的输出(假如显示有问题的话请调整终端大小)"),
                        Static(Pretty(DATA, indent_guides=True), classes="pretty pad"),
                        SubTitle("JSON"),
                        Window(Static(JSON(JSON_EXAMPLE), expand=True), classes="pad")
                    ),
                    classes="location-mocoBot location-first",
                ),
                Column(
                    Section(
                        SectionTitle("配置"),
                        TextContent(Markdown(SETUP_MD)),
                        LoginForm(),
                    ),
                    classes="location-setup",
                ),

                # Column(
                #     Section(
                #         SectionTitle("CSS"),
                #         TextContent(Markdown(CSS_MD)),
                #         Window(
                #             Static(
                #                 Syntax(
                #                     example_css,
                #                     "css",
                #                     theme="material",
                #                     line_numbers=True,
                #                 ),
                #                 expand=True,
                #             )
                #         ),
                #     ),
                #     classes="location-css",
                # ),
            ),
        )
        yield Footer()

    def action_open_link(self, link: str) -> None:
        self.app.bell()
        import webbrowser

        webbrowser.open(link)

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        self.set_focus(None)
        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            if sidebar.query("*:focus"):
                self.screen.set_focus(None)
            sidebar.add_class("-hidden")

    def on_mount(self) -> None:
        self.add_note("MocoBot is running")

        self.query_one("Welcome Button", Button).focus()

    def action_screenshot(self, filename: str | None = None, path: str = "./screenshot/") -> None:
        """Save an SVG "screenshot". This action will save an SVG file containing the current contents of the screen.

        Args:
            filename: Filename of screenshot, or None to auto-generate.
            path: Path to directory.
        """
        folder = os.path.exists("screenshot")
        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs("screenshot")  # makedirs 创建文件时如果路径不存在会创建这个路径
        self.bell()
        path = self.save_screenshot(filename, path)
        message = f"截图保存至 [bold green]'{escape(str(path))}'[/]"
        self.add_note(Text.from_markup(message))
        self.notify(message)


app = SetupApp()
if __name__ == "__main__":
    app.run()
