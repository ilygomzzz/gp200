import QtQuick

// Compact cell art (< 1100 px): the unit's rendered thumbnail centred on the floor line (y 112), no text labels.
Item {
    id: ac
    property string block: ""
    property var info: null
    property bool on: false
    readonly property var u: R.units && info ? R.units[info.key] : undefined
    anchors.fill: parent
    Image {
        visible: ac.u !== undefined && ac.u.thumb !== undefined
        source: visible ? T.render_dir + ac.u.thumb : ""; sourceSize: Qt.size(256, 256); mipmap: true; asynchronous: true
        width: 108; height: 108; x: (ac.width - width) / 2; y: 112 - height + 6; opacity: ac.on ? 1 : 0.55
    }
    Contact { wide: 84; x: (ac.width - width) / 2; y: 100; strength: T.tex_shadow }
}
