import QtQuick

Rectangle {
    id: pb
    signal chooseSlot()
    signal editEffect()
    property bool compactHint: false
    readonly property bool open: board.open
    readonly property int count: open ? 13 : 2
    readonly property real gap1: 8  // one-row gap: jacks are 40 px cells, units 92
    readonly property real fit: Math.min(1, width / (80 + 11 * T.cell_w + 12 * gap1 + 32))
    readonly property bool oneRow: open && fit >= 0.87  // else wrap (min cell ~80 px)
    readonly property real sc: oneRow ? fit : 1
    readonly property real gapW: oneRow ? gap1 : T.cell_gap
    readonly property int n: oneRow ? count : Math.max(1, Math.floor((width - 32 + 12) / 104))
    readonly property int rows: Math.ceil(count / n)
    property int dropGap: -1
    implicitHeight: oneRow ? (T.cell_h + 32) * sc : rows * T.cell_h + (rows - 1) * 16 + 32
    radius: T.r_plate
    color: T.plate
    border.color: T.plate_border

    function isJack(i) { return i === 0 || i === count - 1 }
    function cx(i) {
        if (oneRow) return 16 + (i === 0 ? 0 : 40 + gap1 + (i - 1) * (T.cell_w + gap1))
        return 16 + (i % n) * (T.cell_w + T.cell_gap) + (isJack(i) ? 26 : 0)
    }
    function cy(i) { return 16 + Math.floor(i / n) * (T.cell_h + 16) }
    function gapAt(x, y) {  // chain gap (0..11, before unit j) nearest to a board point
        var best = 0, bd = 1e9
        for (var k = 0; k < 12; k++) {
            var d = Math.hypot(x - (cx(k + 1) - gapW / 2), y - (cy(k + 1) + 56))
            if (d < bd) { bd = d; best = k }
        }
        return best
    }

    Item {
        id: field
        width: pb.width / pb.sc; height: pb.height / pb.sc
        scale: pb.sc; transformOrigin: Item.TopLeft
        Jack { x: pb.cx(0); y: pb.cy(0); label: "Guitarra" }
        Jack { x: pb.cx(pb.count - 1); y: pb.cy(pb.count - 1); label: "Salida" }
        Repeater {
            model: pb.open ? 12 : 1
            Cable {
                readonly property int to: pb.open ? index + 1 : 1
                readonly property string blk: index > 0 ? board.order[index - 1] : ""
                x0: pb.cx(index) + (index === 0 ? 40 : 84); y0: pb.cy(index) + 72
                x1: pb.cx(to) + (to === pb.count - 1 ? 0 : 8); y1: pb.cy(to) + 72
                wrap: pb.cy(index) !== pb.cy(to)
                lit: pb.open && !board.loading && (index === 0 || (board.units[blk] !== undefined && board.units[blk].on))
                color: index === 0 ? T.dim : T.block_colors[blk]
            }
        }
        Repeater {
            model: board.blocks
            Unit {
                required property string modelData
                block: modelData
                visible: pb.open
                info: board.units[modelData] === undefined ? null : board.units[modelData]
                selected: board.selected === modelData
                readonly property int idx: board.order.indexOf(modelData) + 1
                slotX: pb.cx(idx); slotY: pb.cy(idx)
                onSelectReq: board.select(modelData)
                onToggleReq: { board.select(modelData); board.toggle(modelData) }
                onMoveReq: function (d) { board.move(modelData, d) }
                onNeighbour: function (d) { var o = board.order, j = o.indexOf(modelData) + d; if (j >= 0 && j < o.length) board.select(o[j]) }
                onEditEffect: { board.select(modelData); pb.editEffect() }
                onDragMoved: function (px, py) { board.select(modelData); var g = pb.gapAt(px, py), i = board.order.indexOf(modelData); pb.dropGap = (g === i || g === i + 1) ? -1 : g }
                onDragEnd: function (commit) { if (commit && pb.dropGap >= 0) board.moveTo(modelData, pb.dropGap); pb.dropGap = -1 }
            }
        }
        Rectangle {
            visible: pb.dropGap >= 0
            width: 3; height: 112; radius: 1.5; color: T.accent
            z: 20; x: pb.cx(pb.dropGap + 1) - pb.gapW / 2 - 1.5; y: pb.cy(pb.dropGap + 1) + 4
        }
    }
    Column {
        visible: !pb.open
        anchors.centerIn: parent
        spacing: T.s2
        Text { anchors.horizontalCenter: parent.horizontalCenter; text: T.glyphs.empty; font.family: T.icon_font; font.pixelSize: 48; color: T.ink_off }
        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Elige un slot para ver su cadena"; color: T.dim; font.pixelSize: T.font_body; font.family: T.font }
        Btn { visible: pb.compactHint; anchors.horizontalCenter: parent.horizontalCenter; text: "Elegir slot"; onClicked: pb.chooseSlot() }
    }
    Rectangle {  // indeterminate bar while saving / Claude runs
        id: busyBar
        visible: board.busy !== ""
        x: 24; y: 0; width: parent.width - 48; height: 2; color: T.ink_off; clip: true
        Rectangle {
            width: parent.width * 0.3; height: 2; color: T.accent
            SequentialAnimation on x { running: busyBar.visible; loops: Animation.Infinite
                NumberAnimation { from: -busyBar.width * 0.3; to: busyBar.width; duration: T.motion ? 1200 : 1 } }
        }
    }
}
