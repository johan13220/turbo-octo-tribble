"""Search screen — domain input, provider selection, launch analysis."""
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.textfield import MDTextField


class SearchContent(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = "vertical"
        self.padding = [dp(16), dp(24), dp(16), dp(16)]
        self.spacing = dp(14)
        self._provider = "scraper"

        self.add_widget(MDLabel(
            text="SEO Dashboard",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(52),
            bold=True,
        ))
        self.add_widget(MDLabel(
            text="Analyse any domain's SEO health",
            font_style="Body2",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(28),
        ))

        self.domain_field = MDTextField(
            hint_text="Domain (e.g. example.com)",
            icon_right="web",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
        )
        self.add_widget(self.domain_field)

        # Provider card
        card = MDCard(
            padding=dp(14),
            size_hint_y=None,
            height=dp(130),
            radius=[dp(8)],
            elevation=2,
        )
        card_col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        card_col.add_widget(MDLabel(
            text="Data Provider",
            font_style="Overline",
            size_hint_y=None,
            height=dp(24),
        ))

        for label, key, default_active in [
            ("SEMrush API (requires key)", "semrush", False),
            ("On-page Scraper (no key needed)", "scraper", True),
        ]:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(8))
            cb = MDCheckbox(group="provider", active=default_active, size_hint=(None, None), size=(dp(36), dp(36)))
            _key = key
            cb.bind(active=lambda widget, val, k=_key: self._on_provider(k, val))
            row.add_widget(cb)
            row.add_widget(MDLabel(text=label))
            card_col.add_widget(row)

        card.add_widget(card_col)
        self.add_widget(card)

        self.analyze_btn = MDRaisedButton(
            text="ANALYSE",
            size_hint=(1, None),
            height=dp(50),
        )
        self.analyze_btn.bind(on_press=self._on_analyse)
        self.add_widget(self.analyze_btn)

        # Loading row
        loading_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50),
                                   spacing=dp(12), pos_hint={"center_x": 0.5})
        self.spinner = MDSpinner(size_hint=(None, None), size=(dp(32), dp(32)), active=False)
        loading_row.add_widget(self.spinner)
        self.status_label = MDLabel(text="", font_style="Body2", theme_text_color="Secondary")
        loading_row.add_widget(self.status_label)
        self.add_widget(loading_row)

        self.add_widget(Widget())

    def _on_provider(self, key: str, active: bool) -> None:
        if active:
            self._provider = key

    def _on_analyse(self, *args) -> None:
        domain = self.domain_field.text.strip()
        if not domain:
            self.status_label.text = "Please enter a domain."
            return
        self.status_label.text = f"Analysing {domain}..."
        self.app.run_analysis(domain, self._provider)

    def show_loading(self, loading: bool) -> None:
        self.spinner.active = loading
        self.analyze_btn.disabled = loading
        if not loading:
            from android_ui import state
            if state.state.error:
                self.status_label.text = f"Error: {state.state.error}"
            elif state.state.domain:
                self.status_label.text = f"Done: {state.state.domain}"
