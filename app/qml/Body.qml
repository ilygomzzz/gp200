import QtQuick

// A lit enclosure: key light top-left (enamel gradient, 1 px highlights top/left, shaded right strip) + optional material tile.
Rectangle {
    id: b
    property string tex: ""
    property real texOp: 0
    property bool hover: false
    Tex { visible: b.tex !== ""; src: b.tex; op: b.texOp; inset: b.radius * 0.3 }
    Rectangle {
        anchors.fill: parent; radius: b.radius
        gradient: Gradient { GradientStop { position: 0; color: T.face_hi } GradientStop { position: 0.5; color: "transparent" } GradientStop { position: 1; color: T.face_lo } }
    }
    Rectangle { x: b.radius; y: 0; width: parent.width - 2 * b.radius; height: 1; color: T.bevel_hi }
    Rectangle { x: 0; y: b.radius; width: 1; height: parent.height - 2 * b.radius; color: T.bevel_hi }
    Rectangle { x: parent.width - 3; y: b.radius; width: 3; height: parent.height - 2 * b.radius; color: T.face_lo }
    Rectangle { anchors.fill: parent; radius: b.radius; color: T.face_hi; visible: b.hover }
}
