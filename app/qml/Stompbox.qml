import QtQuick
import QtQuick.Effects

Item {
    id: sb
    property string block: ""
    property bool on: false
    property bool ghost: false
    property var mini: []
    readonly property color col: T.block_colors[block] || T.dim
    width: T.cell_w; height: 112
    Rectangle {
        id: body
        x: 8; y: 8; width: 76; height: 104; radius: T.r_unit
        color: sb.ghost ? "transparent" : Qt.tint(T.chassis_base, Qt.alpha(sb.col, 0.6))
        border.width: sb.ghost ? 1 : 0; border.color: T.ink_off
        layer.enabled: T.fx && !sb.ghost
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: T.shadow; shadowBlur: 0.4; shadowVerticalOffset: 3 }
        Rectangle {  // enamel: lit top, shaded bottom
            visible: !sb.ghost; anchors.fill: parent; radius: parent.radius
            gradient: Gradient { GradientStop { position: 0; color: T.face_hi } GradientStop { position: 0.5; color: "transparent" } GradientStop { position: 1; color: T.face_lo } }
        }
        Rectangle { visible: !sb.ghost; x: 8; y: 1; width: parent.width - 16; height: 1; color: T.bevel_hi }
    }
    Row {
        visible: !sb.ghost
        x: 8 + (76 - width) / 2; y: 20; spacing: 8
        Repeater { model: sb.mini; Knob { mini: true; dia: T.knob_mini; from: 0; to: 1; value: modelData } }
    }
    Rectangle {  // dark print band: block colour stays legible on any paint
        visible: !sb.ghost
        x: 14; y: 42; width: 64; height: 20; radius: 4; color: T.nameplate
        Row {
            anchors.centerIn: parent; spacing: 4
            Text { text: T.glyphs[sb.block] || ""; font.family: T.icon_font; font.pixelSize: 14; color: sb.col; anchors.verticalCenter: parent.verticalCenter }
            Text { text: sb.block; font.pixelSize: T.font_small; font.weight: Font.DemiBold; font.letterSpacing: T.track_code; font.family: T.font; color: sb.col; anchors.verticalCenter: parent.verticalCenter }
        }
    }
    Led { visible: !sb.ghost; x: 8 + 38 - 4; y: 68; on: sb.on; color: sb.col }
    Footswitch { visible: !sb.ghost; x: 8 + 38 - 12; y: 84; size: 24; interactive: false; on: sb.on }
}
