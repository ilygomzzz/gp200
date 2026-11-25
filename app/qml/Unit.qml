import QtQuick
import QtQuick.Controls

FocusScope {
    id: u
    property string block: ""
    property var info: null
    property bool selected: false
    property bool ghost: info === null
    property bool dragging: false
    property real slotX: 0
    property real slotY: 0
    property real dragX: 0
    property real dragY: 0
    signal selectReq()
    signal toggleReq()
    signal moveReq(int delta)
    signal editEffect()
    signal neighbour(int delta)
    signal dragMoved(real px, real py)
    signal dragEnd(bool commit)
    readonly property bool on: info !== null && info.on
    x: dragging ? dragX : slotX
    y: dragging ? dragY : slotY
    Behavior on x { enabled: !u.dragging; NumberAnimation { duration: T.dur_m; easing.type: Easing.OutCubic } }
    Behavior on y { enabled: !u.dragging; NumberAnimation { duration: T.dur_m; easing.type: Easing.OutCubic } }
    width: T.cell_w; height: T.cell_h
    scale: dragging ? 1.05 : 1
    z: dragging ? 10 : 0
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: ghost ? block : block + " · " + info.effect + " · " + (on ? "encendido" : "apagado")
    Keys.onPressed: function (e) {
        if (ghost) return
        if (e.key === Qt.Key_Space) toggleReq()
        else if (e.key === Qt.Key_Escape && dragging) { dragging = false; area.cancelled = true; dragEnd(false) }
        else if (e.key === Qt.Key_Left || e.key === Qt.Key_Right) {
            var d = e.key === Qt.Key_Left ? -1 : 1
            if (e.modifiers & Qt.ControlModifier) moveReq(d); else neighbour(d)
        }
        else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) editEffect()
        else return
        e.accepted = true
    }
    Rectangle { anchors.fill: parent; radius: T.r_unit; color: area.containsMouse && !u.dragging ? T.sel_fill : "transparent"
        border.width: u.selected || u.activeFocus ? 2 : 0; border.color: T.accent; opacity: u.selected ? 1 : 0.6 }
    Rectangle { visible: u.ghost; anchors.fill: parent; anchors.margins: 8; radius: 6; color: "transparent"; border.width: 1; border.color: T.ink_off; opacity: T.ghost_op }  // ghost: outline in place
    ArtCell { visible: !u.ghost; block: u.block; info: u.info; on: u.on }
    Text {
        visible: !u.ghost
        y: 116; x: 4; width: parent.width - 8; horizontalAlignment: Text.AlignHCenter
        text: u.ghost ? "" : u.info.effect; elide: Text.ElideRight; color: T.dim; font.pixelSize: T.font_small; font.family: T.font
    }
    MouseArea {
        id: area
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        property real px: 0
        property real py: 0
        property bool moved: false
        property bool cancelled: false
        onPressed: function (m) {
            u.forceActiveFocus()
            if (m.button === Qt.RightButton) { menu.popup(); return }
            px = m.x; py = m.y; moved = false; cancelled = false
        }
        onPositionChanged: function (m) {
            if (!pressed || u.ghost || cancelled || !(pressedButtons & Qt.LeftButton)) return
            if (!u.dragging && Math.hypot(m.x - px, m.y - py) > 8) { moved = true; u.dragging = true; u.dragX = u.slotX; u.dragY = u.slotY }
            if (u.dragging) {
                var p = mapToItem(u.parent, m.x, m.y)
                u.dragX = p.x - px; u.dragY = p.y - py
                u.dragMoved(p.x, p.y)
            }
        }
        onReleased: function (m) { if (u.dragging) { u.dragging = false; u.dragEnd(!cancelled) } }
        onClicked: function (m) {
            if (m.button !== Qt.LeftButton || moved || u.ghost) return
            if (m.y > 76 && m.y < 112) u.toggleReq(); else u.selectReq()
        }
        onDoubleClicked: if (!u.ghost && !moved) u.toggleReq()
    }
    Menu {
        id: menu
        MenuItem { text: "Mover a la izquierda"; onTriggered: u.moveReq(-1) }
        MenuItem { text: "Mover a la derecha"; onTriggered: u.moveReq(1) }
        MenuItem { text: u.on ? "Apagar" : "Encender"; onTriggered: u.toggleReq() }
        MenuItem { text: "Cambiar efecto…"; onTriggered: u.editEffect() }
    }
}
