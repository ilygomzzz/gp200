import QtQuick
import QtQuick.Shapes

Shape {
    id: c
    property real x0: 0
    property real y0: 0
    property real x1: 0
    property real y1: 0
    property bool wrap: false
    property bool lit: false
    property color color: T.dim
    readonly property string d: {
        if (!wrap) {
            var dx = (x1 - x0) / 3
            return "M " + x0 + " " + y0 + " C " + (x0 + dx) + " " + (y0 + 16) + " " + (x1 - dx) + " " + (y1 + 16) + " " + x1 + " " + y1
        }
        var r = 8, gx = x0 + 12, gx2 = x1 - 12, gy = y0 + 80
        return "M " + x0 + " " + y0 + " L " + (gx - r) + " " + y0 + " Q " + gx + " " + y0 + " " + gx + " " + (y0 + r)
            + " L " + gx + " " + (gy - r) + " Q " + gx + " " + gy + " " + (gx - r) + " " + gy
            + " L " + (gx2 + r) + " " + gy + " Q " + gx2 + " " + gy + " " + gx2 + " " + (gy + r)
            + " L " + gx2 + " " + (y1 - r) + " Q " + gx2 + " " + y1 + " " + (gx2 + r) + " " + y1 + " L " + x1 + " " + y1
    }
    ShapePath { strokeColor: T.cable; strokeWidth: 5; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathSvg { path: c.d } }
    ShapePath { strokeColor: c.lit ? Qt.alpha(c.color, 0.7) : T.ink_off; strokeWidth: 2; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathSvg { path: c.d } }
}
