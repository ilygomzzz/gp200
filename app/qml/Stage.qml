import QtQuick
import QtQuick.Shapes

// The rig scene, authored in stage units (T.stage_w x T.stage_h) and scaled uniformly by the caller via `s`.
// Layers (z): wall 0, mat 1, spotlight 2, back line 4, cables 5, pedalboard 6, floor 8, jack plates 9.
Item {
    id: st
    property real s: 0.7
    readonly property bool labels: 18 * s >= 12  // text authored at 18 su: hide it when it would fall below 12 px
    readonly property bool ghost: !board.open || board.loading
    readonly property var zones: ({ AMP: [355, 12, 345, 110], CAB: [355, 122, 345, 218], MOD: [912, 112, 276, 55], DLY: [912, 172, 276, 55],
        RVB: [912, 232, 276, 55], PRE: [372, 366, 96, 132], DST: [520, 366, 96, 132], NR: [668, 398, 76, 100], EQ: [796, 366, 96, 132],
        WAH: [944, 366, 104, 140], VOL: [1100, 366, 104, 140] })
    readonly property var sel: zones[board.selected] || zones.AMP
    width: T.stage_w; height: T.stage_h
    scale: s; transformOrigin: Item.TopLeft
    opacity: board.busy !== "" ? 0.6 : 1
    enabled: board.busy === ""

    function unitFor(b) { return units.count > 0 ? units.itemAt(board.blocks.indexOf(b)) : null }
    function outPt(k) {
        if (k === 0) return Qt.point(84, 440)
        var u = unitFor(board.order[k - 1])
        return u ? Qt.point(u.outX, u.outY) : Qt.point(0, 0)
    }
    function inPt(k) {
        if (k === 11) return Qt.point(1480, 236)
        var u = unitFor(board.order[k])
        return u ? Qt.point(u.inX, u.inY) : Qt.point(0, 0)
    }

    Item {  // clip: the whole scene lives inside the rounded stage
        anchors.fill: parent
        clip: true
        Rectangle { id: wall; width: parent.width; height: T.stage_h * T.stage_horizon + 20; radius: 16; color: T.stage_wall; z: 0
            Shape { anchors.fill: parent
                ShapePath { strokeColor: "transparent"
                    fillGradient: RadialGradient { centerX: 520; centerY: 0; centerRadius: 1100; focalX: 520; focalY: 0
                        GradientStop { position: 0; color: T.stage_wall_hi } GradientStop { position: 1; color: T.stage_wall } }
                    PathRectangle { x: 0; y: 0; width: 1600; height: 330 } } }
        }
        Rectangle { y: T.stage_h * T.stage_horizon; width: parent.width; height: T.stage_h - y; radius: 16; color: T.stage_mat; z: 1 }
        Rectangle { y: T.stage_h * T.stage_horizon; width: parent.width; height: 24; color: T.stage_mat; z: 1 }  // square the mat's top corners
        Tex { x: 0; y: T.stage_h * T.stage_horizon; width: parent.width; height: T.stage_h - y; anchors.fill: undefined; src: "stage_mat"; op: T.tex_mat; z: 1 }
        Rectangle { y: T.stage_h * T.stage_horizon; width: parent.width; height: 24; z: 1
            gradient: Gradient { GradientStop { position: 0; color: T.face_lo } GradientStop { position: 1; color: "transparent" } } }
        Rectangle { y: T.stage_h * T.stage_horizon; width: parent.width; height: 1; color: T.bevel_hi; z: 1 }
        Image {  // key light from the top-left: a soft spot following the selection
            z: 2; source: T.tex_dir + "spot.png"; width: 640; height: 420; opacity: T.tex_spot; smooth: true
            x: st.sel[0] + st.sel[2] / 2 - 320; y: -60
            Behavior on x { NumberAnimation { duration: T.dur_m; easing.type: Easing.OutCubic } }
        }
        // ---- rack case + stand ----
        Item { z: 3
            Repeater { model: [924, 1166]; Rectangle { required property real modelData; x: modelData; y: 300; width: 9; height: 40; color: T.metal_dark } }
            Rectangle { x: 928; y: 326; width: 244; height: 6; color: T.metal_dark }
            Contact { x: 900 - 20; y: 322; wide: 340 }
        }
        Body { z: 3; x: 900; y: 100; width: 300; height: 207; radius: 8; color: T.chassis.rack_dark.body; tex: "tolex"; texOp: T.tex_tolex
            Rectangle { x: 10; y: 10; width: 280; height: 187; color: T.stage_wall }
            Repeater { model: [10, 189]; Item { required property real modelData
                Rectangle { x: 2; y: modelData; width: 296; height: 8; color: T.chassis.rack_dark.face }
                Repeater { model: 18; Rectangle { required property int index; x: 8 + index * 16; y: modelData + 2.5; width: 3; height: 3; radius: 1.5; color: T.metal_dark } } } }
        }
        // ---- pedalboard ----
        Body { z: 6; x: 300; y: 356; width: 1000; height: 152; radius: 12; color: T.board_tolex; tex: "tread"; texOp: T.tex_tread }
        Repeater { model: [492, 500]; Rectangle { required property real modelData; z: 6; x: 300; y: modelData; width: 1000; height: 4; color: T.rail
            Tex { src: "brushed"; op: T.tex_brushed } } }
        // ---- jack plates ----
        Item { z: 9
            Rectangle { x: 28; y: 432; width: 60; height: 16; radius: 3; color: T.metal; border.width: 1; border.color: T.metal_dark }
            Rectangle { x: 84; y: 436; width: 10; height: 8; color: T.metal_dark }
            Text { visible: st.labels; x: 10; y: 452; text: "Guitarra"; font.pixelSize: 18; font.family: T.font; color: T.dim }
            Body { x: 1480; y: 200; width: 48; height: 72; radius: 6; color: T.metal; tex: "brushed"; texOp: T.tex_brushed
                Rectangle { x: 16; y: 28; width: 16; height: 16; radius: 8; color: T.cable; border.width: 2; border.color: T.metal_dark } }
            Text { visible: st.labels; x: 1470; y: 276; text: "Salida"; font.pixelSize: 18; font.family: T.font; color: T.dim }
        }
        // ---- cables (chain order) ----
        Item {
            id: cables
            z: 7; visible: board.open
            Repeater {
                model: 12
                Wire {
                    required property int index
                    readonly property string src: index > 0 ? board.order[index - 1] : ""
                    readonly property string dst: index < 11 ? board.order[index] : ""
                    p0: st.outPt(index); p1: st.inPt(index)
                    stub: src === "AMP" && dst === "CAB"
                    lit: !st.ghost && (index === 0 || (board.units[src] !== undefined && board.units[src].on))
                    color: index === 0 ? T.dim : T.block_colors[src]
                }
            }
            property string seen: ""
            SequentialAnimation { id: fade
                NumberAnimation { target: cables; property: "opacity"; to: 0.3; duration: T.dur_m / 2 }
                NumberAnimation { target: cables; property: "opacity"; to: 1; duration: T.dur_m / 2 } }
            Connections { target: board; function onChainChanged() { var o = board.order.join(); if (cables.seen !== "" && o !== cables.seen) fade.restart(); cables.seen = o } }
        }
        // ---- units ----
        Repeater {
            id: units
            model: board.blocks
            SceneUnit {
                required property string modelData
                block: modelData
                z: back ? 7.5 : 8
                zone: st.zones[modelData]
                ghost: st.ghost
                labels: st.labels
                info: board.units[modelData] === undefined ? null : board.units[modelData]
                selected: board.open && board.selected === modelData
                onSelectReq: board.select(modelData)
                onToggleReq: { board.select(modelData); board.toggle(modelData) }
                onMoveReq: function (d) { board.move(modelData, d) }
                onEditEffect: { board.select(modelData); st.editEffect() }
            }
        }
    }
    signal editEffect()
}
