import QtQuick

Rectangle {
    id: pill
    visible: error || text !== ""  // no orphan icon-only pill
    property string text: ""
    property bool error: false
    implicitHeight: 28
    implicitWidth: row.implicitWidth + 24
    radius: height / 2
    color: T.plate
    border.color: T.plate_border
    Row {
        id: row
        anchors.centerIn: parent
        spacing: T.s2
        Text {
            visible: pill.error || pill.text !== ""
            text: pill.error ? T.glyphs.error : pill.text.endsWith("…") ? T.glyphs.busy : T.glyphs.ok
            font.family: T.icon_font; font.pixelSize: T.font_small
            color: pill.error ? T.danger : T.dim
        }
        Text {
            text: pill.text; font.pixelSize: T.font_small; font.family: T.font
            color: pill.error ? T.danger : T.text
            width: Math.min(implicitWidth, (pill.parent ? pill.parent.width : 400) - 80); elide: Text.ElideRight
        }
    }
}
