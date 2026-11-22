import QtQuick
import QtQuick.Controls

Popup {
    id: pop
    property string name: ""
    property string valueText: ""
    width: 96; height: 56; padding: 0
    closePolicy: Popup.NoAutoClose
    focus: false
    enter: Transition { NumberAnimation { property: "opacity"; from: 0; to: 1; duration: T.dur_s } }
    exit: Transition { NumberAnimation { property: "opacity"; from: 1; to: 0; duration: T.motion ? 150 : 0 } }
    background: Rectangle { color: T.popup_bg; radius: T.r_tile; border.color: T.sel_border }
    contentItem: Column {
        anchors.centerIn: parent
        Text { text: pop.name; color: T.dim; font.pixelSize: T.font_small; font.family: T.font; anchors.horizontalCenter: parent.horizontalCenter }
        Text { text: pop.valueText; color: T.text; font.pixelSize: T.font_value; font.family: T.mono; anchors.horizontalCenter: parent.horizontalCenter }
    }
}
