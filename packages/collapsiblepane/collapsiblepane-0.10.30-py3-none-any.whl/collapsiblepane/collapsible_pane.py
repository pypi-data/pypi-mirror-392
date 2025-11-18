from typing import Optional, Union
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QParallelAnimationGroup,
    QAbstractAnimation, QEasingCurve, QRect, Signal
)
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QSizePolicy,
    QGraphicsOpacityEffect, QFrame, QLabel,
    QHBoxLayout, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor, QIcon


class CollapsiblePane(QWidget):
    toggled: Signal = Signal(bool)

    def __init__(self, title: str = "", animation_duration: int = 150, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._text_style = ""
        self.animation_duration: int = animation_duration
        self._expanded: bool = False
        self._use_qicon: bool = False
        self._collapsed_icon: Union[str, QIcon] = "▸"
        self._expanded_icon: Union[str, QIcon] = "▾"

        # --- Header Frame ---
        self.header_frame: QFrame = QFrame(self)
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.header_frame.setCursor(Qt.PointingHandCursor)
        self.header_frame.setAutoFillBackground(True)

        self.header_layout: QHBoxLayout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(10, 4, 10, 4)
        self.header_layout.setSpacing(8)

        self.chevron_label: QLabel = QLabel(self._collapsed_icon)
        self.chevron_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.title_label: QLabel = QLabel(title)
        self.title_label.setStyleSheet("QLabel{font-size: 14px; font-weight: 600; color: white;}")

        self.count_label: QLabel = QLabel("")
        self.count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.count_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 12px;
            }
        """)

        self.header_layout.addWidget(self.chevron_label)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.count_label)

        self.header_frame.setStyleSheet("""
            QFrame#header_frame {
                background-color: #28a745;
                border-radius: 8px;
            }
        """)

        # --- Content Area ---
        self.content_area: QScrollArea = QScrollArea(self)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        # --- Fade opacity effect ---
        self.opacity_effect: QGraphicsOpacityEffect = QGraphicsOpacityEffect(self.content_area)
        self.content_area.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation: QPropertyAnimation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(self.animation_duration)

        # --- Main Layout ---
        self.main_layout: QGridLayout = QGridLayout(self)
        self.main_layout.setVerticalSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.header_frame, 0, 0)
        self.main_layout.addWidget(self.content_area, 1, 0)

        # --- Animations ---
        self.toggle_animation: QParallelAnimationGroup = QParallelAnimationGroup(self)
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.content_area, b"maximumHeight"))
        self.toggle_animation.addAnimation(self.opacity_animation)

        # --- Click handler ---
        self.header_frame.mousePressEvent = lambda e: self.toggle(not self._expanded)

        # --- Header children ---
        self.chevron_label.setAttribute(Qt.WA_TranslucentBackground)
        self.title_label.setAttribute(Qt.WA_TranslucentBackground)

    # -------------------------------------------------------------------------
    # Content and header management
    # -------------------------------------------------------------------------
    def set_content_widget(self, widget: QWidget) -> None:
        """Attach content widget inside the collapsible area."""
        if self.content_area.widget():
            old = self.content_area.widget()
            self.content_area.takeWidget()
            old.deleteLater()
        self.content_area.setWidget(widget)
        widget.adjustSize()

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def set_header_style(
        self,
        background_color: str = "#28a745",
        text_color: str = "white",
        border_color: str = "transparent",
        border_width: int = 0,
        border_radius: int = 0,
        padding_vertical: int = 0,
        padding_horizontal: int = 0,
        font_size: int = 14,
        font_weight: str = "600",
        hover_color: Optional[str] = None
    ) -> None:
        """Customize the header look dynamically."""
        hover_block = f"""
        QFrame#header_frame:hover {{
            background-color: {hover_color};
        }}
        """ if hover_color else ""

        self.header_frame.setStyleSheet(f"""
            QFrame#header_frame {{
                background-color: {background_color};
                border: {border_width}px solid {border_color};
                border-radius: {border_radius}px;
                padding: {padding_vertical}px {padding_horizontal}px;
                background-clip: border;
            }}
            {hover_block}
        """)

        self.title_label.setStyleSheet(
            f"color: {text_color}; font-size: {font_size}px; font-weight: {font_weight};"
        )

    # -------------------------------------------------------------------------
    # Chevron / Icon customization
    # -------------------------------------------------------------------------
    def set_chevron_icons(self, collapsed_icon: Union[str, QIcon], expanded_icon: Union[str, QIcon]) -> None:
        """Set custom icons or text for the chevron."""
        image_exts = (".svg", ".png", ".jpg", ".jpeg", ".bmp", ".ico")

        if isinstance(collapsed_icon, QIcon) and isinstance(expanded_icon, QIcon):
            self._use_qicon = True
            self._collapsed_icon = collapsed_icon
            self._expanded_icon = expanded_icon
            self.chevron_label.setPixmap(collapsed_icon.pixmap(16, 16))

        elif isinstance(collapsed_icon, str) and collapsed_icon.lower().endswith(image_exts):
            self._use_qicon = True
            self._collapsed_icon = QIcon(collapsed_icon)
            self._expanded_icon = QIcon(expanded_icon)
            self.chevron_label.setPixmap(self._collapsed_icon.pixmap(16, 16))

        else:
            self._use_qicon = False
            self._collapsed_icon = collapsed_icon
            self._expanded_icon = expanded_icon
            self.chevron_label.setText(self._collapsed_icon)

    # -------------------------------------------------------------------------
    # Styling helpers
    # -------------------------------------------------------------------------
    def set_card_style(self, background: str = "#ffffff", border: str = "#00000020",
                       radius: int = 0, padding: int = 0, shadow_only: bool = False) -> None:
        """Customize expanded area style dynamically."""
        if shadow_only:
            self.content_area.setAutoFillBackground(True)
            self.content_area.setAttribute(Qt.WA_TranslucentBackground, True)

        self._card_style = f"""
            QScrollArea{{
                background-color: {background};
                border: 1px solid {border};
                border-radius: {radius}px;
                padding: {padding}px;
            }}
        """
        self.content_area.setStyleSheet(self._card_style)

    def set_card_shadow(self, color: str = "#000000", blur: int = 20, offset_y: int = 4) -> None:
        """Add a drop shadow under the expanded content."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset_y)
        shadow.setColor(QColor(color))
        self.content_area.setGraphicsEffect(shadow)

    def set_content_text_style(self, color: str = "#333333", font_size: int = 13) -> None:
        """Change default text styling for the content area."""
        self._text_style = f"color: {color}; font-size: {font_size}px;"
        content = self.content_area.widget()
        if content:
            content.setStyleSheet(self._text_style)

    def set_title_style(self, color: str = "#FFFFFF", font_size: int = 14,
                        font_weight: str = "600", italic: bool = False) -> None:
        """Style the title text dynamically."""
        style = f"""
            color: {color};
            font-size: {font_size}px;
            font-weight: {font_weight};
            {'font-style: italic;' if italic else ''}
        """
        self.title_label.setStyleSheet(style)

    def set_item_count(self, count: Optional[int], show_badge: bool = True) -> None:
        """Display an item count badge."""
        if count is None or not show_badge:
            self.count_label.setText("")
            self.count_label.setStyleSheet("")
            return

        self.count_label.setText(f"Items: {count}")
        self.set_item_badge_style()

    def set_item_badge_style(
        self,
        text: Optional[str] = None,
        bg_color: str = "rgba(0,120,215,0.15)",
        text_color: str = "#0078d7",
        border_color: str = "rgba(0,120,215,0.5)",
        border_radius: int = 8,
        padding_vertical: int = 0,
        padding_horizontal: int = 0,
        font_size: int = 12,
        font_weight: str = "600",
        shadow: bool = False,
        min_width: int = 28
    ) -> None:
        """Dynamically style the badge (count label)."""
        if text is not None:
            self.count_label.setText(str(text))

        self.count_label.setAutoFillBackground(True)
        self.count_label.setAttribute(Qt.WA_TranslucentBackground, False)

        style = f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: {border_radius}px;
                border: 1px solid {border_color};
                padding: {padding_vertical}px {padding_horizontal}px;
                font-size: {font_size}px;
                font-weight: {font_weight};
                min-width: {min_width}px;
                text-align: center;
                qproperty-alignment: AlignCenter;
            }}
        """
        self.count_label.setStyleSheet(style)

        if shadow:
            shadow_effect = QGraphicsDropShadowEffect(self.count_label)
            shadow_effect.setBlurRadius(10)
            shadow_effect.setOffset(0, 2)
            shadow_effect.setColor(QColor(0, 0, 0, 40))
            self.count_label.setGraphicsEffect(shadow_effect)
        else:
            self.count_label.setGraphicsEffect(None)

    # -------------------------------------------------------------------------
    # Behavior controls
    # -------------------------------------------------------------------------
    def set_collapsed(self, collapsed: bool = True) -> None:
        """Force collapse/expand without animation."""
        self._expanded = not collapsed
        if collapsed:
            self.content_area.setMaximumHeight(0)
            self.setMaximumHeight(self.header_frame.sizeHint().height())
            self.chevron_label.setText(self._collapsed_icon if not self._use_qicon else "")
        else:
            content = self.content_area.widget()
            if content:
                content_height = content.sizeHint().height()
                self.content_area.setMaximumHeight(content_height)
                self.setMaximumHeight(self.header_frame.sizeHint().height() + content_height)
            self.chevron_label.setText(self._expanded_icon if not self._use_qicon else "")

    # -------------------------------------------------------------------------
    # Animation toggle
    # -------------------------------------------------------------------------
    def toggle(self, expand: bool) -> None:
        """Animate expanding or collapsing."""
        if self._expanded == expand:
            return
        self._expanded = expand
        self.toggled.emit(expand)

        if self._use_qicon:
            icon = self._expanded_icon if expand else self._collapsed_icon
            if isinstance(icon, QIcon):
                self.chevron_label.setPixmap(icon.pixmap(16, 16))
        else:
            self.chevron_label.setText(self._expanded_icon if expand else self._collapsed_icon)

        content = self.content_area.widget()
        if not content:
            return

        content.adjustSize()
        content_height = content.sizeHint().height()
        collapsed_height = self.header_frame.sizeHint().height()

        for i in range(self.toggle_animation.animationCount() - 1):
            anim = self.toggle_animation.animationAt(i)
            anim.setStartValue(collapsed_height)
            anim.setEndValue(collapsed_height + content_height)
            anim.setDuration(self.animation_duration)
            anim.setEasingCurve(QEasingCurve.OutCubic)

        content_anim = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        content_anim.setStartValue(0)
        content_anim.setEndValue(content_height)
        content_anim.setDuration(self.animation_duration)
        content_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.opacity_animation.setStartValue(0.0 if expand else 1.0)
        self.opacity_animation.setEndValue(1.0 if expand else 0.0)

        direction = QAbstractAnimation.Forward if expand else QAbstractAnimation.Backward
        self.toggle_animation.setDirection(direction)
        self.toggle_animation.start()

        try:
            self.toggle_animation.finished.disconnect()
        except TypeError:
            pass

        def on_finished() -> None:
            if not expand:
                self.content_area.setMaximumHeight(0)
                self.setMaximumHeight(collapsed_height)
            else:
                self.content_area.setMaximumHeight(content_height)

        self.toggle_animation.finished.connect(on_finished)
