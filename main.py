import secrets
import string

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.textinput import TextInput
from kivy.utils import platform


BACKGROUND = (16 / 255, 19 / 255, 28 / 255, 1)
CARD = (25 / 255, 29 / 255, 41 / 255, 1)
FIELD = (17 / 255, 20 / 255, 29 / 255, 1)
TEXT = (241 / 255, 243 / 255, 249 / 255, 1)
MUTED = (166 / 255, 173 / 255, 192 / 255, 1)
ACCENT = (152 / 255, 133 / 255, 1, 1)


def generate_random_password(
    length: int,
    lowercase: bool = True,
    uppercase: bool = True,
    digits: bool = True,
    symbols: bool = True,
) -> str:
    """Generate a cryptographically secure password using the selected character groups."""
    groups = []
    if lowercase:
        groups.append(string.ascii_lowercase)
    if uppercase:
        groups.append(string.ascii_uppercase)
    if digits:
        groups.append(string.digits)
    if symbols:
        groups.append(string.punctuation)

    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("Длина пароля должна быть целым числом.")
    if not 1 <= length <= 128:
        raise ValueError("Длина пароля должна быть от 1 до 128 символов.")
    if not groups:
        raise ValueError("Выберите хотя бы один набор символов.")
    if length < len(groups):
        raise ValueError("Длина пароля меньше количества выбранных наборов символов.")

    alphabet = "".join(groups)
    password = [secrets.choice(group) for group in groups]
    password.extend(secrets.choice(alphabet) for _ in range(length - len(password)))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


class FluGeneratorApp(App):
    title = "FluGenerator"

    def build(self) -> BoxLayout:
        Window.clearcolor = BACKGROUND
        if platform != "android":
            Window.size = (420, 760)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["bars", "content"],
        )
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(14),
            padding=(dp(24), dp(28), dp(24), dp(24)),
        )
        card.bind(minimum_height=card.setter("height"))
        with card.canvas.before:
            Color(*CARD)
            self.card_background = RoundedRectangle(
                radius=[dp(22)],
                pos=card.pos,
                size=card.size,
            )
        card.bind(
                pos=lambda *args: setattr(self.card_background, "pos", args[1]),
                size=lambda *args: setattr(self.card_background, "size", args[1]),
        )

        self._add_label(card, "FLUGENERATOR", color=ACCENT, height=dp(24), bold=True)
        self._add_label(card, "Генератор паролей", height=dp(44), font_size="24sp", bold=True)
        self._add_label(
            card,
            "Надёжный случайный пароль — прямо в приложении.",
            color=MUTED,
            height=dp(44),
        )

        length_row = BoxLayout(size_hint_y=None, height=dp(34))
        length_row.add_widget(Label(text="Длина пароля", color=TEXT, halign="left", valign="middle"))
        self.length_value = Label(
            text="16",
            color=ACCENT,
            bold=True,
            size_hint_x=None,
            width=dp(44),
        )
        length_row.add_widget(self.length_value)
        card.add_widget(length_row)

        self.length_slider = Slider(
            min=8,
            max=128,
            value=16,
            step=1,
            size_hint_y=None,
            height=dp(38),
        )
        self.length_slider.bind(value=self._on_length_changed)
        card.add_widget(self.length_slider)

        self.options: dict[str, CheckBox] = {}
        options_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(3),
            row_default_height=dp(45),
            row_force_default=True,
        )
        options_layout.bind(minimum_height=options_layout.setter("height"))
        options_layout.add_widget(
            Label(
                text="Какие символы использовать",
                color=TEXT,
                size_hint_y=None,
                height=dp(36),
                halign="left",
                valign="middle",
            )
        )
        for key, title in (
            ("lowercase", "Строчные буквы  (a–z)"),
            ("uppercase", "Заглавные буквы  (A–Z)"),
            ("digits", "Цифры  (0–9)"),
            ("symbols", "Специальные символы  (!@#…)"),
        ):
            self.options[key] = self._add_option(options_layout, title)
        card.add_widget(options_layout)

        self.result = TextInput(
            hint_text="Ваш пароль появится здесь",
            readonly=True,
            multiline=False,
            halign="center",
            size_hint_y=None,
            height=dp(58),
            font_size="16sp",
            foreground_color=TEXT,
            hint_text_color=MUTED,
            background_normal="",
            background_active="",
            background_color=FIELD,
            padding=(dp(12), dp(18)),
        )
        card.add_widget(self.result)

        generate_button = Button(
            text="Сгенерировать пароль",
            size_hint_y=None,
            height=dp(52),
            bold=True,
            color=BACKGROUND,
            background_normal="",
            background_down="",
            background_color=ACCENT,
        )
        generate_button.bind(on_release=self._generate)
        card.add_widget(generate_button)

        self.copy_button = Button(
            text="Скопировать пароль",
            size_hint_y=None,
            height=dp(50),
            disabled=True,
            background_normal="",
            background_down="",
            background_color=(52 / 255, 57 / 255, 77 / 255, 1),
            color=TEXT,
        )
        self.copy_button.bind(on_release=self._copy)
        card.add_widget(self.copy_button)

        self.status = Label(
            text="",
            color=ACCENT,
            size_hint_y=None,
            height=dp(38),
            halign="center",
            valign="middle",
        )
        card.add_widget(self.status)
        scroll.add_widget(card)

        # ── История: пароли нигде не сохраняются ──────────────────────
        history_scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["bars", "content"],
        )
        history_panel = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(14),
            padding=(dp(24), dp(28), dp(24), dp(24)),
        )
        history_panel.bind(minimum_height=history_panel.setter("height"))
        with history_panel.canvas.before:
            Color(*CARD)
            self.history_background = RoundedRectangle(
                radius=[dp(22)],
                pos=history_panel.pos,
                size=history_panel.size,
            )
        history_panel.bind(
            pos=lambda *args: setattr(self.history_background, "pos", args[1]),
            size=lambda *args: setattr(self.history_background, "size", args[1]),
        )

        self._add_label(
            history_panel,
            "ИСТОРИЯ",
            color=ACCENT,
            height=dp(24),
            bold=True,
        )
        self._add_label(
            history_panel,
            "Пароли не сохраняются",
            height=dp(44),
            font_size="24sp",
            bold=True,
        )
        self._add_label(
            history_panel,
            "FluGenerator не хранит сгенерированные пароли. Каждый пароль создаётся "
            "локально на устройстве и не записывается ни в историю, ни в файл, ни в "
            "облако. После закрытия приложения восстановить его невозможно.",
            color=MUTED,
            height=dp(110),
        )
        self._add_label(
            history_panel,
            "Почему так сделано",
            height=dp(36),
            font_size="18sp",
            bold=True,
        )
        self._add_label(
            history_panel,
            "• Нет серверов и синхронизации — пароли никуда не отправляются.\n"
            "• Нет доступа в интернет: приложение генерирует пароль офлайн.\n"
            "• Нет логов и кэша — даже разработчик не может их посмотреть.\n"
            "• Буфер обмена очищается при закрытии приложения.",
            color=MUTED,
            height=dp(130),
        )
        self._add_label(
            history_panel,
            "Совет: сохраните один надёжный пароль в менеджере паролей "
            "(Bitwarden, KeePass), а для остальных сайтов генерируйте новый каждый раз.",
            color=TEXT,
            height=dp(80),
        )
        history_scroll.add_widget(history_panel)

        # ── Вкладки ───────────────────────────────────────────────────
        tab_panel = TabbedPanel(do_default_tab=False, tab_width=dp(150))
        with tab_panel.canvas.before:
            Color(*BACKGROUND)
            self.tabs_background = RoundedRectangle(
                radius=[dp(0)],
                pos=tab_panel.pos,
                size=tab_panel.size,
            )
        tab_panel.bind(
            pos=lambda *args: setattr(self.tabs_background, "pos", args[1]),
            size=lambda *args: setattr(self.tabs_background, "size", args[1]),
        )

        generator_tab = TabbedPanelHeader(text="Генератор")
        generator_tab.content = scroll
        tab_panel.add_widget(generator_tab)

        history_tab = TabbedPanelHeader(text="История")
        history_tab.content = history_scroll
        tab_panel.add_widget(history_tab)

        return tab_panel

    @staticmethod
    def _add_label(
        parent: BoxLayout,
        text: str,
        color: tuple[float, float, float, float] = TEXT,
        height: float = dp(28),
        font_size: str = "16sp",
        bold: bool = False,
    ) -> None:
        label = Label(
            text=text,
            color=color,
            size_hint_y=None,
            height=height,
            font_size=font_size,
            bold=bold,
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda widget, value: setattr(widget, "text_size", value))
        parent.add_widget(label)

    def _add_option(self, parent: GridLayout, title: str) -> CheckBox:
        row = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(10),
            padding=(dp(10), 0),
        )
        checkbox = CheckBox(
            active=True,
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            color=ACCENT,
        )
        checkbox.bind(active=self._on_option_changed)
        label = Label(
            text=title,
            color=TEXT,
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda widget, value: setattr(widget, "text_size", value))
        row.add_widget(checkbox)
        row.add_widget(label)
        parent.add_widget(row)
        return checkbox

    def _on_length_changed(self, slider: Slider, value: float) -> None:
        if int(slider.value) != int(value):
            return
        self.length_value.text = str(int(value))
        self._invalidate_result()

    def _on_option_changed(self, checkbox: CheckBox, active: bool) -> None:
        if checkbox.active != active:
            return
        self._invalidate_result()
        if not active and not any(option.active for option in self.options.values()):
            self.status.text = "Выберите хотя бы один набор символов."

    def _invalidate_result(self) -> None:
        if hasattr(self, "result"):
            self.result.text = ""
            self.copy_button.disabled = True
            self.status.text = ""

    def _generate(self, button: Button) -> None:
        if button.disabled:
            return
        try:
            password = generate_random_password(
                int(self.length_slider.value),
                **{name: checkbox.active for name, checkbox in self.options.items()},
            )
        except (TypeError, ValueError) as error:
            self._invalidate_result()
            self.status.text = str(error)
            return

        self.result.text = password
        self.copy_button.disabled = False
        self.status.text = "Новый пароль готов."

    def _copy(self, button: Button) -> None:
        if button.disabled or not self.result.text:
            self.copy_button.disabled = True
            self.status.text = "Сначала сгенерируйте пароль."
            return

        Clipboard.copy(self.result.text)
        self.status.text = "Пароль скопирован."

    def on_stop(self) -> bool:
        # Приложение ничего не хранит: при закрытии очищаем буфер обмена,
        # чтобы последний сгенерированный пароль не остался доступен другим программам.
        Clipboard.copy("")
        return False


if __name__ == "__main__":
    FluGeneratorApp().run()
