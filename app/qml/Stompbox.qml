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
        x: 8; y: 8; width: 76; height: 104; radius: 10
        color: sb.ghost ? "transparent" : Qt.tint(T.chassis_base, Qt.alpha(sb.col, 0.6))
        border.width: sb.ghost ? 1 : 0; border.color: T.ink_off
        layer.enabled: T.fx && !sb.ghost
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: T.shadow; shadowBlur: 0.4; shadowVerticalOffset: 3 }
        Rectangle { visible: !sb.ghost; x: 8; y: 1; width: parent.width - 16; height: 1; color: T.bevel_hi }
    }
    Row {
        visible: !sb.ghost
        x: 8 + (76 - width) / 2; y: 20; spacing: 8
        Repeater { model: sb.mini; Knob { mini: true; dia: T.knob_mini; from: 0; to: 1; value: modelData } }
    }
    Row {
        visible: !sb.ghost
        x: 8; y: 44; width: 76; spacing: 4
        layoutDirection: Qt.LeftToRight
        Item { width: (76 - glyph.width - code.width - 4) / 2; height: 1 }
        Text { id: glyph; text: T.glyphs[sb.block] || ""; font.family: T.icon_font; font.pixelSize: 16; color: T.ink_dark }
        Text { id: code; text: sb.block; font.pixelSize: T.font_small; font.bold: true; font.family: T.font; color: T.ink_dark }
    }
    Led { visible: !sb.ghost; x: 8 + 38 - 4; y: 68; on: sb.on; color: sb.col }
    Footswitch { visible: !sb.ghost; x: 8 + 38 - 10; y: 84; size: 20; interactive: false; on: sb.on }
}
