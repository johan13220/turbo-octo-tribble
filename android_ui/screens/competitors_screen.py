"""Competitor analysis screen."""
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, ThreeLineListItem


def _fmt(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, int) and val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    if isinstance(val, int) and val >= 1_000:
        return f"{val / 1_000:.1f}K"
    return str(val)


class CompetitorCard(MDCard):
    def __init__(self, snapshot, **kwargs):
        super().__init__(
            padding=dp(14),
            size_hint_y=None,
            height=dp(110),
            radius=[dp(8)],
            elevation=2,
            **kwargs,
        )
        col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        col.add_widget(MDLabel(
            text=snapshot.domain,
            font_style="Subtitle1",
            bold=True,
        ))
        grid = MDGridLayout(cols=3, size_hint_y=None, height=dp(50), spacing=dp(8))
        for label, value in [
            ("Authority", _fmt(snapshot.authority_score)),
            ("Traffic", _fmt(snapshot.organic_traffic)),
            ("Keywords", _fmt(snapshot.organic_keywords)),
        ]:
            cell = MDBoxLayout(orientation="vertical")
            cell.add_widget(MDLabel(text=value, font_style="H6", halign="center", bold=True))
            cell.add_widget(MDLabel(text=label, font_style="Caption", halign="center",
                                     theme_text_color="Secondary"))
            grid.add_widget(cell)
        col.add_widget(grid)
        self.add_widget(col)


class CompetitorsContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(10)

        self.title = MDLabel(
            text="Competitor Analysis",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
        )
        self.add_widget(self.title)

        scroll = ScrollView()
        self.comp_list = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        self.comp_list.bind(minimum_height=self.comp_list.setter("height"))
        scroll.add_widget(self.comp_list)
        self.add_widget(scroll)

    def refresh(self) -> None:
        from android_ui import state
        competitors = state.state.competitors
        self.comp_list.clear_widgets()

        if not competitors:
            self.comp_list.add_widget(MDLabel(
                text="No competitor data.\nSEMrush API required.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(80),
            ))
            return

        self.title.text = f"Top {len(competitors)} Competitors"
        for snap in competitors:
            self.comp_list.add_widget(CompetitorCard(snap))
