import QtQuick
import QtQuick.Controls

ToolTip {
    id: tip
    delay: 500
    contentItem: Text { text: tip.text; color: T.text; font.pixelSize: T.font_small; font.family: T.font }
    background: Rectangle { color: T.popup_bg; border.color: T.sel_border; radius: T.s2 }
}
