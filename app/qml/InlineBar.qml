import QtQuick
import QtQuick.Layouts

Rectangle {
    id: bar
    default property alias content: row.data
    property string text: ""
    implicitHeight: 48
    radius: T.r_tile
    color: T.plate
    border.color: T.plate_border
    Rectangle { width: T.s1; height: parent.height - 16; y: 8; radius: 2; color: T.warn }
    RowLayout {
        id: row
        anchors { fill: parent; leftMargin: T.s4; rightMargin: T.s4 }
        spacing: T.s3
        Text { text: bar.text; color: T.text; font.pixelSize: T.font_body; font.family: T.font }
    }
}
