import QtQuick
import QtQuick.Controls

// The signal chain as 11 chips under the stage (real px): reorder lives here (drag, Ctrl+Left/Right, menu). Tab order = chain order.
Item {
    id: cs
    signal editEffect()
    readonly property int n: 11
    readonly property real cw: Math.min(96, (width - (n - 1) * 4) / n)
    readonly property bool skeleton: !board.open || board.loading
    property int dropGap: -1
    height: T.chip_h + 8
    opacity: board.busy !== "" ? 0.6 : 1
    enabled: board.busy === ""
    function slotX(i) { return (width - (n * cw + (n - 1) * 4)) / 2 + i * (cw + 4) }
    function gapAt(px) {  // chain gap 0..11 nearest to a strip x
        var best = 0, bd = 1e9
        for (var k = 0; k <= n; k++) { var d = Math.abs(px - (k === 0 ? slotX(0) - 2 : slotX(k - 1) + cw + 2)); if (d < bd) { bd = d; best = k } }
        return best
    }
    Rectangle { x: slotX(0) + cw / 2; y: T.chip_h / 2 - 1; width: slotX(n - 1) - slotX(0); height: 2; color: T.ink_off }  // the signal
    Repeater {
        model: board.order
        FocusScope {
            id: chip
            required property string modelData
            required property int index
            property bool dragging: false
            property real dragX: 0
            readonly property var info: board.units[modelData]
            readonly property bool on: !!info && info.on
            readonly property color col: T.block_colors[modelData] || T.dim
            x: dragging ? dragX : cs.slotX(index); y: dragging ? -2 : 0; width: cs.cw; height: T.chip_h
            z: dragging ? 10 : 0
            scale: dragging ? 1.05 : 1
            Behavior on x { enabled: !chip.dragging; NumberAnimation { duration: T.dur_m; easing.type: Easing.OutCubic } }
            activeFocusOnTab: !cs.skeleton
            Accessible.role: Accessible.Button
            Accessible.name: info ? modelData + " · " + info.effect + " · " + (on ? "encendido" : "apagado") : modelData
            Keys.onPressed: function (e) {
                if (cs.skeleton) return
                if (e.key === Qt.Key_Space) board.toggle(modelData)
                else if (e.key === Qt.Key_Escape && chip.dragging) { chip.dragging = false; area.cancelled = true; cs.dropGap = -1 }
                else if (e.key === Qt.Key_Left || e.key === Qt.Key_Right) {
                    var d = e.key === Qt.Key_Left ? -1 : 1
                    if (e.modifiers & Qt.ControlModifier) board.move(modelData, d)
                    else { var j = index + d; if (j >= 0 && j < board.order.length) board.select(board.order[j]) }
                }
                else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { board.select(modelData); cs.editEffect() }
                else return
                e.accepted = true
            }
            Rectangle { anchors.fill: parent; radius: T.r_pill; color: T.nameplate
                border.width: board.selected === chip.modelData && !cs.skeleton ? 2 : 0; border.color: T.accent }
            Rectangle { visible: chip.activeFocus; anchors.fill: parent; anchors.margins: -3; radius: T.r_pill; color: "transparent"; border.width: 2; border.color: Qt.alpha(T.accent, 0.4) }
            Rectangle { visible: cs.skeleton; x: (parent.width - width) / 2; y: 12; width: parent.width * 0.6; height: 8; radius: 4; color: T.ink_off }
            Row {
                visible: !cs.skeleton
                anchors.centerIn: parent; spacing: 4
                Rectangle { width: 6; height: 6; radius: 3; anchors.verticalCenter: parent.verticalCenter; color: chip.on ? chip.col : T.led_off }
                Text { text: T.glyphs[chip.modelData] || ""; font.family: T.icon_font; font.pixelSize: 14; color: chip.on ? chip.col : T.ink_soft; anchors.verticalCenter: parent.verticalCenter }
                Text { visible: cs.cw >= 64; text: chip.modelData; font.pixelSize: T.font_small; font.weight: Font.DemiBold; font.letterSpacing: T.track_code; font.family: T.font
                    color: chip.on ? chip.col : T.ink_soft; anchors.verticalCenter: parent.verticalCenter }
            }
            MouseArea {
                id: area
                anchors.fill: parent
                enabled: !cs.skeleton
                hoverEnabled: true
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                property real px: 0
                property bool moved: false
                property bool cancelled: false
                onPressed: function (m) {
                    chip.forceActiveFocus()
                    if (m.button === Qt.RightButton) { board.select(chip.modelData); menu.popup(); return }
                    px = m.x; moved = false; cancelled = false
                }
                onPositionChanged: function (m) {
                    if (!pressed || cancelled || !(pressedButtons & Qt.LeftButton)) return
                    if (!chip.dragging && Math.abs(m.x - px) > 8) { moved = true; chip.dragging = true; chip.dragX = cs.slotX(chip.index) }
                    if (chip.dragging) {
                        var p = mapToItem(cs, m.x, m.y)
                        chip.dragX = p.x - px
                        board.select(chip.modelData)
                        var g = cs.gapAt(p.x)
                        cs.dropGap = (g === chip.index || g === chip.index + 1) ? -1 : g
                    }
                }
                onReleased: function (m) {
                    if (!chip.dragging) return
                    chip.dragging = false
                    var g = cs.dropGap
                    cs.dropGap = -1
                    if (!cancelled && g >= 0) board.moveTo(chip.modelData, g)
                }
                onClicked: function (m) { if (m.button === Qt.LeftButton && !moved) board.select(chip.modelData) }
                onDoubleClicked: if (!moved) board.toggle(chip.modelData)
                Tip { text: chip.info ? chip.modelData + " · " + chip.info.effect + " · " + (chip.on ? "encendido" : "apagado") : ""; delay: 600; visible: area.containsMouse && !!chip.info && !chip.dragging }
            }
            Menu {
                id: menu
                MenuItem { text: "Mover a la izquierda"; onTriggered: board.move(chip.modelData, -1) }
                MenuItem { text: "Mover a la derecha"; onTriggered: board.move(chip.modelData, 1) }
                MenuItem { text: chip.on ? "Apagar" : "Encender"; onTriggered: board.toggle(chip.modelData) }
                MenuItem { text: "Cambiar efecto…"; onTriggered: { board.select(chip.modelData); cs.editEffect() } }
            }
        }
    }
    Rectangle { visible: cs.dropGap >= 0; width: 3; height: T.chip_h; radius: 1.5; color: T.accent; z: 20
        x: (cs.dropGap === 0 ? cs.slotX(0) - 2 : cs.slotX(cs.dropGap - 1) + cs.cw + 2) - 1.5 }
}
