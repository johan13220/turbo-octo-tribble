"""Overview screen — domain metrics + top keywords list."""
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, TwoLineListItem


def _fmt(val, suffix: str = "") -> str:
    if val is None:
        return "N/A"
    if isinstance(val, int) and val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M{suffix}"
    if isinstance(val, int) and val >= 1_000:
        return f"{val / 1_000:.1f}K{suffix}"
    return f"{val}{suffix}"


class MetricCard(MDCard):
    def __init__(self, label: str, value: str = "—", **kwargs):
        super().__init__(
            padding=dp(10),
            size_hint_y=None,
            height=dp(80),
            radius=[dp(8)],
            elevation=2,
            **kwargs,
        )
        col = MDBoxLayout(orientation="vertical")
        self.value_lbl = MDLabel(
            text=value, font_style="H5", halign="center", bold=True
        )
        col.add_widget(self.value_lbl)
        col.add_widget(MDLabel(
            text=label,
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary",
        ))
        self.add_widget(col)

    def set_value(self, value: str) -> None:
        self.value_lbl.text = value


class OverviewContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(10)

        self.title = MDLabel(
            text="Enter a domain and press Analyse",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(44),
        )
        self.add_widget(self.title)

        # 2×2 metric grid (+ optional GSC row)
        self.grid = MDGridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(180),
            spacing=dp(8),
            padding=[0, 0, 0, 0],
        )
        self._cards: dict[str, MetricCard] = {}
        for label, key in [
            ("Authority", "authority"),
            ("Traffic / mo", "traffic"),
            ("Keywords", "keywords"),
            ("Backlinks", "backlinks"),
        ]:
            card = MetricCard(label)
            self._cards[key] = card
            self.grid.add_widget(card)
        self.add_widget(self.grid)

        # Optional GSC row
        self._gsc_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(90),
            spacing=dp(8),
        )
        self._gsc_clicks = MetricCard("GSC Clicks")
        self._gsc_impr = MetricCard("Impressions")
        self._gsc_pos = MetricCard("Avg Position")
        self._gsc_row.add_widget(self._gsc_clicks)
        self._gsc_row.add_widget(self._gsc_impr)
        self._gsc_row.add_widget(self._gsc_pos)
        # hidden by default
        self._gsc_row.height = 0
        self._gsc_row.opacity = 0
        self.add_widget(self._gsc_row)

        # Keywords section
        self.kw_section_label = MDLabel(
            text="",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(32),
        )
        self.add_widget(self.kw_section_label)

        scroll = ScrollView()
        self.kw_list = MDList()
        scroll.add_widget(self.kw_list)
        self.add_widget(scroll)

    def refresh(self) -> None:
        from android_ui import state
        overview = state.state.overview
        keywords = state.state.keywords
        domain = state.state.domain

        if not overview:
            return

        self.title.text = f"Overview — {domain}"
        self._cards["authority"].set_value(_fmt(overview.authority_score))
        self._cards["traffic"].set_value(_fmt(overview.organic_traffic))
        self._cards["keywords"].set_value(_fmt(overview.organic_keywords))
        self._cards["backlinks"].set_value(_fmt(overview.backlinks_total))

        # GSC fields
        if overview.total_clicks is not None:
            self._gsc_clicks.set_value(_fmt(overview.total_clicks))
            self._gsc_impr.set_value(_fmt(overview.total_impressions))
            self._gsc_pos.set_value(
                f"{overview.avg_position:.1f}" if overview.avg_position else "—"
            )
            self._gsc_row.height = dp(90)
            self._gsc_row.opacity = 1
        else:
            self._gsc_row.height = 0
            self._gsc_row.opacity = 0

        # Keywords list
        self.kw_list.clear_widgets()
        if keywords:
            self.kw_section_label.text = f"Top {len(keywords)} Keywords"
            for kw in keywords[:30]:
                pos = f"#{kw.position}" if kw.position else "?"
                if kw.clicks is not None:
                    detail = f"Pos {pos}  ·  {kw.clicks} clicks  ·  CTR {kw.ctr or 0:.1f}%"
                elif kw.search_volume is not None:
                    detail = f"Pos {pos}  ·  Vol {_fmt(kw.search_volume)}"
                else:
                    detail = f"Pos {pos}"
                self.kw_list.add_widget(TwoLineListItem(
                    text=kw.keyword,
                    secondary_text=detail,
                ))
        else:
            self.kw_section_label.text = "No keyword data (SEMrush API or GSC required)"
