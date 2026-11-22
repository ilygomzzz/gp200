import QtQuick

Item {
    id: fs
    property real size: 20
    property bool on: false
    property bool interactive: true
    signal clicked()
    width: size; height: size
    scale: area.pressed ? 0.94 : 1
    Accessible.role: Accessible.Button
    Accessible.name: on ? "Apagar" : "Encender"
    Rectangle { anchors.fill: parent; radius: width / 2; color: T.metal_dark }
    Rectangle { anchors { fill: parent; margins: size * 0.12 } radius: width / 2; color: T.metal; border.color: T.metal_dark; border.width: 1 }
    MouseArea { id: area; anchors.fill: parent; enabled: fs.interactive; onClicked: fs.clicked(); cursorShape: Qt.PointingHandCursor }
    Tip { text: fs.on ? "Apagar" : "Encender"; visible: fs.interactive && area.containsMouse }
    Accessible.onPressAction: clicked()
}
