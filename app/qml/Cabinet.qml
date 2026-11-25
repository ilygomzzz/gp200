import QtQuick

// Speaker cabinet 300x190: tolex box, grille cloth with faint speaker circles (count from the catalog desc), piping, "4x12" print.
Item {
    id: c
    property var info: null
    property bool on: false
    property bool labels: true
    property bool hover: false
    readonly property var ch: T.chassis[info ? info.family : "grille_black"]
    readonly property int sp: info ? info.speakers : 2
    readonly property int cone: info ? info.cone : 12
    readonly property rect hot: Qt.rect(0, 0, 0, 0)  // no live part: click selects only
    width: 300; height: 190
    Body { anchors.fill: parent; radius: 8; color: ch.body; tex: "tolex"; texOp: T.tex_tolex; hover: c.hover
        Repeater { model: [[0, 0], [276, 0], [0, 166], [276, 166]]; Rectangle { required property var modelData; x: modelData[0]; y: modelData[1]; width: 24; height: 24; radius: 4; color: T.metal_dark; opacity: 0.85
            Rectangle { x: 3; y: 3; width: 18; height: 18; radius: 2; color: c.ch.body } } }
    }
    Rectangle { x: 16; y: 16; width: 268; height: 158; color: ch.face; border.width: 2; border.color: ch.knob }  // grille + piping
    Tex { x: 16; y: 16; width: 268; height: 158; anchors.fill: undefined; src: "grille_weave"; op: T.tex_grille }
    Repeater {
        model: c.sp === 1 ? [[150, 95, 120]] : c.sp === 2 ? [[100, 95, 100], [200, 95, 100]] : [[110, 59, 70], [190, 59, 70], [110, 131, 70], [190, 131, 70]]
        Item {
            required property var modelData
            Rectangle { x: modelData[0] - modelData[2] / 2; y: modelData[1] - modelData[2] / 2; width: modelData[2]; height: width; radius: width / 2; color: "transparent"; border.width: 1; border.color: T.ink_dark; opacity: 0.25 }
            Rectangle { x: modelData[0] - 10; y: modelData[1] - 10; width: 20; height: 20; radius: 10; color: T.ink_dark; opacity: 0.15 }
        }
    }
    Text { visible: c.labels; x: 110; y: 175; width: 80; horizontalAlignment: Text.AlignHCenter; text: c.sp + "x" + c.cone; font.pixelSize: 12; font.family: T.font; color: T.dim }
    Rectangle { x: 16; y: 16; width: 268; height: 158; color: "transparent"; border.width: 1; border.color: T.face_lo }
    Repeater { model: [28, 262]; Rectangle { required property real modelData; x: modelData; y: 186; width: 20; height: 6; radius: 2; color: T.metal_dark } }  // feet
}
