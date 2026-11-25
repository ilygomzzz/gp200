import QtQuick
import QtQuick.Shapes

// Treadle (WAH, VOL) 104x140: base + rocker; the rocker's toe drops as the value falls (heel-down = low); toe LED.
Item {
    id: t
    property string block: ""
    property var info: null
    property bool on: false
    property bool labels: true
    property bool hover: false
    readonly property var ch: T.chassis.treadle_black
    readonly property color col: T.block_colors[block] || T.dim
    readonly property real v: info && info.knobs.length ? info.knobs[0] : 0.5
    readonly property real drop: 20 * (1 - v)
    readonly property rect hot: Qt.rect(70, 0, 34, 40)
    width: 104; height: 140
    Shape {
        id: rocker
        anchors.fill: parent
        ShapePath {
            strokeColor: T.metal_dark; strokeWidth: 1; fillColor: t.ch.face
            startX: 8 + 0; startY: 108
            PathLine { x: 96; y: 108 }
            PathLine { x: 96 - 8; y: 6 + t.drop }
            PathLine { x: 8 + 8; y: 6 + t.drop }
            PathLine { x: 8; y: 108 }
        }
    }
    Tex { x: 20; y: 30 + t.drop; width: 64; height: 72 - t.drop; anchors.fill: undefined; src: "tread"; op: T.tex_tread }
    Rectangle { x: 8; y: 106; width: 88; height: 3; color: T.face_lo }
    Rectangle { x: 96 - 22; y: 12 + t.drop; width: 6; height: 6; radius: 3; color: t.on ? t.col : T.led_off; border.width: t.on ? 0 : 1; border.color: T.bevel_hi }
    Body { y: 104; width: 104; height: 36; radius: 6; color: t.ch.body; tex: "powder"; texOp: T.tex_powder; hover: t.hover
        Rectangle { x: 0; y: 8; width: 4; height: 20; color: T.metal }
        Rectangle { x: 100; y: 8; width: 4; height: 20; color: T.metal }
        Text { visible: t.labels; anchors.centerIn: parent; text: t.block; font.pixelSize: 14; font.weight: Font.DemiBold; font.letterSpacing: T.track_code; font.family: T.font; color: t.col }
    }
}
