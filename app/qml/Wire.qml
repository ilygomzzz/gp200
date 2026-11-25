import QtQuick
import QtQuick.Shapes

// Patch cable between two jack points (stage units): a natural curve (`pts`) that keeps clear of every unit. Width follows depth (manifest `cable_w`), 3 strokes (shadow, body, highlight).
Item {
    id: w
    property point p0: Qt.point(0, 0)
    property point p1: Qt.point(0, 0)
    property bool lit: false
    property color color: T.dim
    property bool stub: false  // head -> cab speaker lead: short, straight
    property int lane: 0
    property var pts: []  // polyline from `board.cable` (art.cable_path): natural curve, never through a unit
    readonly property bool art: R.cable_w !== undefined
    readonly property var poly: stub || pts.length < 2 ? [p0, p1] : pts.map(function (q) { return Qt.point(q[0], q[1]) })
    readonly property real ly: pts.length ? pts.reduce(function (m, q) { return Math.max(m, q[1]) }, 0) : Math.max(p0.y, p1.y)
    readonly property real cw: {  // cable width at this depth, linear in the lowest row
        if (!art) return 6
        var a = R.cable_w[0], b = R.cable_w[1], t = Math.max(0, Math.min(1, (ly - a[0]) / (b[0] - a[0])))
        return a[1] + (b[1] - a[1]) * t
    }
    Shape {
        ShapePath { strokeColor: w.art ? T.cable_shadow : "transparent"; strokeWidth: w.cw * 1.8; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathPolyline { path: w.poly } }
        ShapePath { strokeColor: T.cable; strokeWidth: w.art ? w.cw : 6; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathPolyline { path: w.poly } }
        ShapePath { strokeColor: w.art ? T.cable_hi : "transparent"; strokeWidth: w.cw * 0.28; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathPolyline { path: w.poly } }
        ShapePath { strokeColor: w.lit ? Qt.alpha(w.color, 0.7) : T.ink_off; strokeWidth: w.art ? w.cw * 0.22 : 2; fillColor: "transparent"; capStyle: ShapePath.RoundCap; PathPolyline { path: w.poly } }
    }
    Repeater {  // plugs: rendered sprites when the manifest has them, else the 2B rectangle
        model: w.stub ? [] : [w.p0, w.p1]
        Item {
            required property point modelData
            required property int index
            readonly property var pl: w.art && R.plugs ? R.plugs[index === 0 ? "straight_r" : "straight_l"] : undefined
            Image {
                visible: parent.pl !== undefined; source: parent.pl ? T.render_dir + parent.pl.img : ""; smooth: true
                scale: parent.pl ? parent.pl.su_per_px : 1; transformOrigin: Item.TopLeft
                x: parent.pl ? modelData.x - parent.pl.tip[0] * parent.pl.su_per_px : 0; y: parent.pl ? modelData.y - parent.pl.tip[1] * parent.pl.su_per_px : 0
            }
            Rectangle { visible: parent.pl === undefined; x: modelData.x - 5; y: modelData.y - 8; width: 10; height: 16; radius: 2; color: T.metal; border.width: 1; border.color: T.metal_dark }
        }
    }
}
