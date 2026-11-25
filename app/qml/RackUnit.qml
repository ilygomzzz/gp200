import QtQuick

// 1U rack unit 240x48: brushed face, ears with screws, display with 2 values in the block colour, 3 knobs, power LED.
Item {
    id: r
    property string block: ""
    property var info: null
    property bool on: false
    property bool labels: true
    property bool hover: false
    readonly property var ch: T.chassis.rack_dark
    readonly property color col: T.block_colors[block] || T.dim
    readonly property var ks: info ? info.knobs.slice(0, 3) : []
    readonly property rect hot: Qt.rect(214, 8, 26, 32)
    width: 240; height: 48
    Body { anchors.fill: parent; radius: 3; color: ch.face; tex: "brushed"; texOp: T.tex_brushed; hover: r.hover }
    Repeater {
        model: [0, 226]
        Item {
            required property real modelData
            Rectangle { x: modelData; width: 14; height: 48; color: r.ch.body; border.width: 1; border.color: T.face_lo }
            Rectangle { x: modelData + 5.5; y: 8; width: 3; height: 3; radius: 1.5; color: T.metal_dark }
            Rectangle { x: modelData + 5.5; y: 37; width: 3; height: 3; radius: 1.5; color: T.metal_dark }
        }
    }
    Rectangle {  // display
        x: 20; y: 10; width: 110; height: 28; radius: 3; color: r.ch.display
        Rectangle { width: parent.width; height: 1; color: T.face_lo }
        Rectangle { y: parent.height - 1; width: parent.width; height: 1; color: T.bevel_hi }
        Text { visible: r.labels; anchors.centerIn: parent; width: parent.width - 8; horizontalAlignment: Text.AlignHCenter; fontSizeMode: Text.HorizontalFit; minimumPixelSize: 8; text: r.info ? r.info.displayShort.join(" · ") : ""; font.pixelSize: 12; font.family: T.mono; color: r.col; opacity: r.on ? 1 : 0.35 }
        Rectangle {  // too small to read: level bar of the first value
            visible: !r.labels; x: 6; y: 12; height: 4; radius: 2; color: r.col; opacity: r.on ? 1 : 0.35
            width: 84 * (r.info && r.info.knobs.length ? r.info.knobs[0] : 0)
        }
    }
    Repeater {
        model: r.ks
        Knob { required property real modelData; required property int index; mini: true; dia: 18; width: 18; height: 18; from: 0; to: 1; value: modelData
            x: 138 + index * 29; y: 15; capLo: r.ch.knob; capHi: Qt.lighter(r.ch.knob, 1.5); pointer: r.ch.body }
    }
    Rectangle { x: 223; y: 21; width: 6; height: 6; radius: 3; color: r.on ? r.col : T.led_off; border.width: r.on ? 0 : 1; border.color: T.bevel_hi }
}
