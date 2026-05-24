"""Technical audit screen — health score + issues list."""
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IconLeftWidget, MDList, TwoLineIconListItem
from kivymd.uix.progressbar import MDProgressBar

_SEVERITY = {
    "error":   ("alert-circle",  [0.95, 0.26, 0.21, 1]),
    "warning": ("alert",         [1.00, 0.76, 0.03, 1]),
    "notice":  ("information",   [0.13, 0.59, 0.95, 1]),
}


class AuditContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(10)

        self.title = MDLabel(
            text="Technical Audit",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
        )
        self.add_widget(self.title)

        # Health score card
        score_card = MDCard(
            padding=dp(16),
            size_hint_y=None,
            height=dp(110),
            radius=[dp(8)],
            elevation=2,
        )
        score_col = MDBoxLayout(orientation="vertical", spacing=dp(10))
        self.score_label = MDLabel(
            text="Health Score: —",
            font_style="H6",
            halign="center",
        )
        score_col.add_widget(self.score_label)
        self.progress = MDProgressBar(value=0, max=100, size_hint_y=None, height=dp(12))
        score_col.add_widget(self.progress)
        self.counts_label = MDLabel(
            text="",
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary",
        )
        score_col.add_widget(self.counts_label)
        score_card.add_widget(score_col)
        self.add_widget(score_card)

        # Issues list
        scroll = ScrollView()
        self.issues_list = MDList()
        scroll.add_widget(self.issues_list)
        self.add_widget(scroll)

    def refresh(self) -> None:
        from android_ui import state
        audit = state.state.audit
        if not audit:
            return

        score = audit.health_score
        self.title.text = f"Technical Audit — {state.state.domain}"
        self.score_label.text = f"Health Score: {score:.0f} / 100"
        self.progress.value = score

        if score >= 80:
            self.progress.color = [0.0, 0.78, 0.33, 1]
        elif score >= 50:
            self.progress.color = [1.0, 0.76, 0.03, 1]
        else:
            self.progress.color = [0.95, 0.26, 0.21, 1]

        e, w, n = len(audit.errors), len(audit.warnings), len(audit.notices)
        self.counts_label.text = f"{e} errors  ·  {w} warnings  ·  {n} notices"

        self.issues_list.clear_widgets()
        for issues, sev in [(audit.errors, "error"), (audit.warnings, "warning"), (audit.notices, "notice")]:
            for issue in issues:
                self._add_issue(issue, sev)

        if e == 0 and w == 0 and n == 0:
            self.issues_list.add_widget(TwoLineIconListItem(
                text="No issues found",
                secondary_text="The page looks technically healthy",
            ))

    def _add_issue(self, issue, severity: str) -> None:
        icon_name, color = _SEVERITY.get(severity, ("information", [0.5, 0.5, 0.5, 1]))
        item = TwoLineIconListItem(
            text=issue.description,
            secondary_text=f"{issue.count} occurrence(s)  ·  {issue.category}",
        )
        icon_widget = IconLeftWidget(icon=icon_name)
        icon_widget.text_color = color
        item.add_widget(icon_widget)
        self.issues_list.add_widget(item)
