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
    readonly property bool art: R.plate !== undefined
    function zoneOf(b) {
        var i = board.units[b], u = i && R.units ? R.units[i.key] : undefined
        return u ? u.rect : (art && R.zones && R.zones[b] ? R.zones[b] : zones[b])
    }
    readonly property var sel: zoneOf(board.selected) || zones.AMP
    width: T.stage_w; height: T.stage_h
    scale: s; transformOrigin: Item.TopLeft
    opacity: board.busy !== "" ? 0.6 : 1
    enabled: board.busy === ""

    function allRects() {  // unit zones + the rack stand footprint down to the rug (legs are obstacles too)
        var out = []
        board.blocks.forEach(function (b) {
            var r = zoneOf(b); if (r === undefined) return
            out.push(r)
            var i = board.units[b]
            if (i && i.kind === "rack" && r[1] + r[3] < 506) out.push([r[0] - 16, r[1] + r[3] + 2, r[2] + 32, 506 - r[1] - r[3] - 2])
        })
        return out
    }
    // Cable policy (lead decision): couplers only between neighbouring floor units; ends of the chain run on the rug; everything that
    // touches the amp/rack goes behind the units (starts at a floor unit's back edge); any visible cable that would cross a unit is dropped.
    function grp(b) { var k = board.units[b] ? board.units[b].kind : ""; return k === "head" || k === "cabinet" ? "amp" : k === "rack" ? "rack" : "board" }
    function cablePts(i, p0, p1) {
        var s = i > 0 ? board.order[i - 1] : "", d = i < 11 ? board.order[i] : ""
        var all = st.allRects(), rs = s ? zoneOf(s) : undefined, rd = d ? zoneOf(d) : undefined
        if (i === 0 || i === 11) return board.cable(p0.x, p0.y, p1.x, p1.y, -1, all)
        if (rs === undefined || rd === undefined) return []
        var gs = grp(s), gd = grp(d)
        if (gs === "board" && gd === "board") {
            var gap = rd[0] - (rs[0] + rs[2])
            return gap >= -8 && gap < 40 ? board.cable(p0.x, p0.y, p1.x, p1.y, -1, all) : []
        }
        var a = gs === "board" ? Qt.point(rs[0] + rs[2] / 2, rs[1] + 6) : p0, b = gd === "board" ? Qt.point(rd[0] + rd[2] / 2, rd[1] + 6) : p1
        return board.cable(a.x, a.y, b.x, b.y, 0, [])
    }
    function unitFor(b) { return units.count > 0 ? units.itemAt(board.blocks.indexOf(b)) : null }
    function outPt(k) {
        if (k === 0) return art && R.jacks ? Qt.point(R.jacks.in[0], R.jacks.in[1]) : Qt.point(84, 440)
        var u = unitFor(board.order[k - 1])
        return u ? Qt.point(u.outX, u.outY) : Qt.point(0, 0)
    }
    function inPt(k) {
        if (k === 11) return art && R.jacks ? Qt.point(R.jacks.out[0], R.jacks.out[1]) : Qt.point(1480, 236)
        var u = unitFor(board.order[k])
        return u ? Qt.point(u.inX, u.inY) : Qt.point(0, 0)
    }

    Item {  // clip: the whole scene lives inside the rounded stage
        anchors.fill: parent
        clip: true
        Image { id: plate; visible: st.art; z: 0; source: st.art ? T.render_dir + R.plate : ""; width: T.stage_w; height: T.stage_h; smooth: true }
        Item { visible: !st.art; anchors.fill: parent
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
        }
        Image {  // key light from the top-left: a soft spot following the selection
            z: 2; source: T.tex_dir + "spot.png"; width: 640; height: 420; opacity: st.art ? T.sel_pool : T.tex_spot; smooth: true
            x: st.sel[0] + st.sel[2] / 2 - 320; y: -60
            Behavior on x { NumberAnimation { duration: T.dur_m; easing.type: Easing.OutCubic } }
        }
        // ---- jack plates ----
        Item { z: 9
            Text { visible: st.labels; x: st.art && R.labels ? R.labels.Guitarra[0] : 10; y: st.art && R.labels ? R.labels.Guitarra[1] : 452; text: "Guitarra"; font.pixelSize: 18; font.family: T.font; color: T.dim }
            Text { visible: st.labels; x: st.art && R.labels ? R.labels.Salida[0] : 1470; y: st.art && R.labels ? R.labels.Salida[1] : 276; text: "Salida"; font.pixelSize: 18; font.family: T.font; color: T.dim }
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
                    pts: st.sel === undefined || stub ? [] : st.cablePts(index, p0, p1)
                    stub: src === "AMP" && dst === "CAB"
                    lane: index % 3
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
                zone: st.zoneOf(modelData)
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
