import QtQuick

// Amp head 300x96 (stage units): tolex box, corner protectors, faceplate with up to 6 knobs, pilot jewel, input jack. Original art.
Item {
    id: h
    property var info: null
    property bool on: false
    property bool labels: true
    property bool hover: false
    readonly property var ch: T.chassis[info ? info.family : "graphite"]
    readonly property var ks: info ? info.knobs.slice(0, 6) : []
    readonly property rect hot: Qt.rect(252, 4, 32, 32)
    width: 300; height: 96
    Rectangle { x: 120; y: 0; width: 60; height: 8; radius: 4; color: T.metal_dark }  // handle
    Body { y: 6; width: 300; height: 90; radius: 8; color: h.ch.body; tex: "tolex"; texOp: T.tex_tolex; hover: h.hover
        Repeater { model: [[0, 0], [276, 0], [0, 66], [276, 66]]; Rectangle { required property var modelData; x: modelData[0]; y: modelData[1]; width: 24; height: 24; radius: 4; color: T.metal_dark; opacity: 0.85
            Rectangle { x: 3; y: 3; width: 18; height: 18; radius: 2; color: h.ch.body } } }
    }
    Item {  // control panel
        x: 12; y: 32; width: 276; height: 52
        Rectangle { anchors.fill: parent; radius: 3; color: h.ch.face; border.width: 1; border.color: T.rail }
        Tex { src: "brushed"; op: h.info && ["brit_gold", "copper", "blackface"].indexOf(h.info.family) >= 0 ? 0.15 : T.tex_brushed }
        Text { visible: h.labels; x: 8; y: 0; text: h.info ? h.info.effect : ""; font.pixelSize: 16; font.weight: Font.DemiBold; font.family: T.font; color: h.ch.ink }
        Repeater {
            model: h.ks
            Knob {
                required property real modelData
                required property int index
                mini: true; dia: 22; from: 0; to: 1; value: modelData
                width: 22; height: 22
                x: h.ks.length > 1 ? 14 + index * (276 - 28 - 22) / (h.ks.length - 1) : 127
                y: 27
                capLo: h.ch.knob; capHi: Qt.lighter(h.ch.knob, 1.5); pointer: h.ch.ink
            }
        }
    }
    Rectangle { x: 20; y: 12; width: 8; height: 8; radius: 4; color: T.metal; border.color: T.metal_dark }
    Rectangle {  // pilot jewel (+ the LED rule: nameplate dims when OFF)
        x: 262; y: 12; width: 12; height: 12; radius: 6; color: h.on ? T.pilot : T.led_off; border.width: 1; border.color: T.bevel_hi
    }
}
