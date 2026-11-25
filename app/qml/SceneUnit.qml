import QtQuick
import QtQuick.Controls

// One piece of gear on the stage: draws its kind (same components reused by art cells and close-up), lifts when selected,
// takes click / toggle / context menu. Order lives in the chain strip, so no drag here.
Item {
    id: su
    property string block: ""
    property var info: null
    property var zone: [0, 0, 100, 100]  // x y w h in stage units
    property bool selected: false
    property bool ghost: false
    property bool labels: true
    signal selectReq()
    signal toggleReq()
    signal moveReq(int delta)
    signal editEffect()
    readonly property string kind: info ? info.kind : ({ PRE: "stompbox", DST: "stompbox", NR: "mini", EQ: "eq", WAH: "treadle", VOL: "treadle", AMP: "head", CAB: "cabinet" }[block] || "rack")
    readonly property bool on: info !== null && info.on
    readonly property bool back: kind === "head" || kind === "cabinet" || kind === "rack"
    readonly property real f: ({ head: 300, cabinet: 300, rack: 240 })[kind] ? width / ({ head: 300, cabinet: 300, rack: 240 })[kind] : 1
    readonly property var ru: info && R.units ? R.units[info.key] : undefined  // rendered sprite for this unit, if any
    property real lift: selected && ru === undefined ? 8 : 0
    Behavior on lift { NumberAnimation { duration: T.dur_m; easing.type: Easing.OutCubic } }
    x: zone[0]; y: zone[1] - lift; width: zone[2]; height: zone[3]
    readonly property real outX: ru && ru.out ? ru.out[0] : kind === "head" ? x + width : x + width + 3
    readonly property real outY: ru && ru.out ? ru.out[1] : y + (kind === "head" ? 80 * f : kind === "cabinet" ? 170 * f : kind === "treadle" ? height - 18 : kind === "rack" ? 24 * f : height * 0.4)
    readonly property real inX: ru && ru.in ? ru.in[0] : kind === "head" ? x + 20 * f : kind === "cabinet" ? x + 12 * f : x - 3
    readonly property real inY: ru && ru.in ? ru.in[1] : kind === "head" ? y + 90 * f : kind === "cabinet" ? y + 170 * f : outY
    Accessible.role: Accessible.Button
    Accessible.name: ghost ? block : block + " · " + info.effect + " · " + (on ? "encendido" : "apagado")

    Image {  // wall shadow (back line): same sprite, on the wall, behind the unit
        visible: !su.ghost && su.back && !su.ru; z: -2
        source: T.tex_dir + "shadow_contact.png"; x: 14; y: -8 + su.lift; width: su.width; height: su.height * 0.6; opacity: 0.3
    }
    Contact {  // floor contact shadow stays on the mat while the unit lifts
        visible: !su.ghost && !su.ru; z: -1
        wide: su.width * (su.selected ? 1.1 : 1); strength: su.selected ? 0.45 : T.tex_shadow
        x: (su.width - width) / 2 + 6; y: su.height + su.lift - 12
    }
    Rectangle {  // selection rim light
        visible: su.selected && !su.ghost && !su.ru; z: 1; anchors.fill: parent; anchors.margins: -5; radius: 8; color: "transparent"
        border.width: 2; border.color: T.accent; opacity: 0.85
    }
    Rectangle {  // ghost: dashed outline in place
        visible: su.ghost; anchors.fill: parent; radius: 6; color: "transparent"; border.width: 1; border.color: T.ink_off; opacity: T.ghost_op
    }
    Loader { active: su.ru !== undefined && !su.ghost; sourceComponent: cRender }
    Component { id: cRender; RenderUnit { u: su.ru; info: su.info; on: su.on; labels: su.labels } }
    Rectangle { visible: area.containsMouse && !su.ghost; anchors.fill: parent; radius: 6; color: T.face_hi }  // hover: doubled enamel light
    MouseArea {
        id: area
        anchors.fill: parent
        enabled: !su.ghost
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        cursorShape: Qt.PointingHandCursor
        function inHot(m) {
            if (su.ru) { var w = su.ru.switch; return w !== undefined && m.x + su.ru.rect[0] >= w[0] && m.x + su.ru.rect[0] <= w[0] + w[2] && m.y + su.ru.rect[1] >= w[1] && m.y + su.ru.rect[1] <= w[1] + w[3] }
            return false }
        onClicked: function (m) {
            if (m.button === Qt.RightButton) { su.selectReq(); menu.popup(); return }
            if (inHot(m)) { su.selectReq(); su.toggleReq() } else su.selectReq()
        }
        onDoubleClicked: su.toggleReq()
        Tip { text: su.ghost ? "" : su.block + " · " + su.info.effect + " · " + (su.on ? "encendido" : "apagado"); visible: area.containsMouse && !su.ghost }
    }
    Menu {
        id: menu
        MenuItem { text: "Mover a la izquierda"; onTriggered: su.moveReq(-1) }
        MenuItem { text: "Mover a la derecha"; onTriggered: su.moveReq(1) }
        MenuItem { text: su.on ? "Apagar" : "Encender"; onTriggered: su.toggleReq() }
        MenuItem { text: "Cambiar efecto…"; onTriggered: su.editEffect() }
    }
}
