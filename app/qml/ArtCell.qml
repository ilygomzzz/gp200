import QtQuick

// Compact cell art (< 1100 px): the stage components drawn at cell size, centred on the floor line (y 112), no text labels.
Item {
    id: ac
    property string block: ""
    property var info: null
    property bool on: false
    readonly property string kind: info ? info.kind : "stompbox"
    readonly property var size: ({ stompbox: [96, 132], mini: [96, 132], eq: [96, 132], treadle: [104, 140], head: [300, 96], cabinet: [300, 190], rack: [240, 48] })[kind]
    readonly property real k: Math.min(84 / size[0], 108 / size[1], 1)
    anchors.fill: parent
    Loader {
        id: ld
        width: ac.size[0]; height: ac.size[1]; scale: ac.k; transformOrigin: Item.TopLeft
        x: (ac.width - width * ac.k) / 2; y: 112 - height * ac.k
        sourceComponent: ({ stompbox: cS, mini: cS, eq: cE, treadle: cT, head: cH, cabinet: cC, rack: cR })[ac.kind]
    }
    Contact { wide: ld.width * ac.k + 8; x: (ac.width - width) / 2; y: 100; strength: T.tex_shadow }
    Component { id: cS; Stompbox { x: -8; y: -8; block: ac.block; on: ac.on; mini: ac.info ? ac.info.mini : []; family: ac.info ? ac.info.family : "" } }
    Component { id: cE; EqBox { info: ac.info; on: ac.on } }
    Component { id: cT; Treadle { block: ac.block; info: ac.info; on: ac.on; labels: false } }
    Component { id: cH; AmpHead { info: ac.info; on: ac.on; labels: false } }
    Component { id: cC; Cabinet { info: ac.info; on: ac.on; labels: false } }
    Component { id: cR; RackUnit { block: ac.block; info: ac.info; on: ac.on; labels: false } }
}
