import QtQuick
import ".."

// Close-up hero: the selected unit's stage component (no second drawing) enlarged above its controls. Skipped for pedal-style kinds.
Item {
    id: h
    property string block: ""
    property var info: null
    readonly property string kind: info ? info.kind : ""
    readonly property var size: ({ head: [300, 96], cabinet: [300, 190], rack: [240, 48], treadle: [104, 140] })[kind]
    readonly property real k: size ? Math.min(height / size[1], width / size[0], 1.6) : 1
    visible: size !== undefined
    Loader {
        width: h.size ? h.size[0] : 0; height: h.size ? h.size[1] : 0; scale: h.k; transformOrigin: Item.TopLeft
        x: h.size ? (h.width - width * h.k) / 2 : 0; y: h.size ? (h.height - height * h.k) / 2 : 0
        sourceComponent: ({ head: cH, cabinet: cC, rack: cR, treadle: cT })[h.kind]
    }
    Component { id: cH; AmpHead { info: h.info; on: h.info !== null && h.info.on; labels: true } }
    Component { id: cC; Cabinet { info: h.info; on: h.info !== null && h.info.on; labels: true } }
    Component { id: cR; RackUnit { block: h.block; info: h.info; on: h.info !== null && h.info.on; labels: true } }
    Component { id: cT; Treadle { block: h.block; info: h.info; on: h.info !== null && h.info.on; labels: true } }
}
