import QtQuick

// EQ stompbox 96x132: 5 fader slots with thumbs at the band values, nameplate, LED, footswitch.
Item {
    id: e
    property string block: "EQ"
    property var info: null
    property bool on: false
    property bool labels: true
    property bool hover: false
    readonly property var ch: T.chassis[info ? info.family : "eq_white"]
    readonly property color col: T.block_colors.EQ
    readonly property rect hot: Qt.rect(24, 98, 48, 34)
    width: 96; height: 132
    Body { anchors.fill: parent; radius: T.r_unit; color: e.ch.body; tex: "powder"; texOp: T.tex_powder; hover: e.hover }
    Repeater {
        model: 5
        Item {
            required property int index
            Rectangle { x: 12 + index * 16; y: 14; width: 6; height: 40; radius: 2; color: T.ink_dark; opacity: 0.6 }
            Rectangle { x: 9 + index * 16; width: 12; height: 6; radius: 1; color: T.metal; border.width: 1; border.color: T.metal_dark
                y: 14 + 40 * (1 - (e.info && index < e.info.knobs.length ? e.info.knobs[index] : 0.5)) - 3 }
        }
    }
    Rectangle { x: 12; y: 64; width: 72; height: 24; radius: 4; color: T.nameplate
        Row { anchors.centerIn: parent; spacing: 4
            Text { text: T.glyphs.EQ; font.family: T.icon_font; font.pixelSize: 14; color: e.col; anchors.verticalCenter: parent.verticalCenter }
            Text { text: "EQ"; font.pixelSize: T.font_small; font.weight: Font.DemiBold; font.letterSpacing: T.track_code; font.family: T.font; color: e.col; anchors.verticalCenter: parent.verticalCenter } } }
    Led { x: 44; y: 92; on: e.on; color: e.col }
    Footswitch { x: 34; y: 102; size: 28; interactive: false; on: e.on }
}
