import QtQuick

Rectangle {
    id: pill
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
            text: pill.error ? T.glyphs.error : pill.text.endsWith("…") ? T.glyphs.busy : T.glyphs.ok
            font.family: T.icon_font; font.pixelSize: T.font_desc
            color: pill.error ? T.danger : T.dim
        }
        Text {
            text: pill.text; font.pixelSize: T.font_desc; font.family: T.font
            color: pill.error ? T.danger : T.text
            width: Math.min(implicitWidth, pill.width - 56); elide: Text.ElideRight
        }
    }
}
