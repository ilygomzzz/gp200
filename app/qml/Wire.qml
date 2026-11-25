import QtQuick
import QtQuick.Shapes

// Patch cable between two jack points (stage units): droops towards the mat, lit in the source block colour when ON.
Item {
    id: w
    property point p0: Qt.point(0, 0)
    property point p1: Qt.point(0, 0)
    property bool lit: false
    property color color: T.dim
    property bool stub: false  // head -> cab speaker lead: short, straight
    readonly property real dx: p1.x - p0.x
    readonly property real ym: Math.max(p0.y, p1.y)
    readonly property real sag: Math.min(120, 24 + 0.15 * Math.abs(dx))
    readonly property real cy: stub ? ym : Math.min(ym + sag, (508 - 0.25 * ym) / 0.75)
    readonly property real arm: Math.min(80, Math.abs(dx) / 2) * (dx >= 0 ? 1 : -1)
    readonly property string d: "M " + p0.x + " " + p0.y + " C " + (p0.x + arm) + " " + cy + " " + (p1.x - arm) + " " + cy + " " + p1.x + " " + p1.y
    Shape {
        ShapePath { strokeColor: T.cable; strokeWidth: 6; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathSvg { path: w.d } }
        ShapePath { strokeColor: w.lit ? Qt.alpha(w.color, 0.7) : T.ink_off; strokeWidth: 2; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathSvg { path: w.d } }
    }
    Repeater {  // plugs
        model: w.stub ? [] : [w.p0, w.p1]
        Rectangle { required property point modelData; x: modelData.x - 5; y: modelData.y - 8; width: 10; height: 16; radius: 2; color: T.metal; border.width: 1; border.color: T.metal_dark }
    }
}
