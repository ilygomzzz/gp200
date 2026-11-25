import QtQuick

// A rendered knob (layers from the manifest `knob_types`): fixed shadow + cap, the mark rotated by `value` (0..1), fixed signed light.
// Centred on (cx, cy) in the parent's units; `r` = cap radius, `sy` = vertical squash of the view.
Item {
    id: ks
    property string type: ""
    property real value: 0
    property real cx: 0
    property real cy: 0
    property real r: 10
    property real sy: 1
    property bool markOnly: false  // the cap is baked into the unit sprite: draw just the rotating pointer
    readonly property var kt: R.knob_types ? R.knob_types[type] : undefined
    readonly property real px: kt ? r / kt.r_px : 0
    visible: kt !== undefined
    x: cx; y: cy
    Item {
        width: 0; height: 0
        transform: Scale { yScale: ks.sy }
        Item {
            width: ks.kt ? ks.kt.px : 0; height: width; scale: ks.px
            x: -width / 2; y: -height / 2
            Image { visible: !ks.markOnly; anchors.fill: parent; source: ks.kt ? T.render_dir + ks.kt.shadow : ""; smooth: true }
            Image { visible: !ks.markOnly; anchors.fill: parent; source: ks.kt ? T.render_dir + ks.kt.cap : ""; smooth: true }
            Image { visible: !ks.markOnly; anchors.fill: parent; source: ks.kt ? T.render_dir + ks.kt.light : ""; smooth: true }
            Image { anchors.fill: parent; source: ks.kt ? T.render_dir + ks.kt.mark : ""; smooth: true
                rotation: ks.kt ? ks.kt.a0 + (ks.kt.a1 - ks.kt.a0) * ks.value : 0 }
        }
    }
}
