import QtQuick
import QtQuick.Controls

Button {
    id: b
    property bool primary: false
    property string glyph: ""
    property string tip: ""
    readonly property bool solid: primary && enabled
    implicitHeight: 32
    implicitWidth: glyph !== "" ? 32 : contentItem.implicitWidth + 32
    padding: 0
    Accessible.name: tip !== "" ? tip : text
    contentItem: Text {
        text: b.glyph !== "" ? b.glyph : b.text
        font.family: b.glyph !== "" ? T.icon_font : T.font
        font.pixelSize: b.glyph !== "" ? 18 : T.font_body
        font.bold: b.primary
        color: b.enabled ? T.text : T.ink_soft
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: height / 2
        color: b.solid ? T.accent : b.hovered && b.enabled ? T.sel_fill : "transparent"
        border.width: b.visualFocus ? 2 : b.glyph !== "" ? 0 : 1
        border.color: b.visualFocus ? T.accent : b.solid ? T.accent : b.enabled ? T.sel_border : T.ink_off
    }
    Tip { text: b.tip; visible: b.tip !== "" && b.hovered }
}
