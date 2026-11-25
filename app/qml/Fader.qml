import QtQuick

// Vertical fader (EQ band): same input rules as Knob (drag, wheel, arrows, Home/End), role Slider.
FocusScope {
    id: f
    property real from: 0
    property real to: 100
    property real step: 1
    property real value: 0
    property string label: ""
    property real defaultValue: from
    property color tint: T.accent
    signal moved(real v)
    readonly property real frac: to > from ? Math.max(0, Math.min(1, (value - from) / (to - from))) : 0
    readonly property int decimals: step >= 1 ? 0 : 2
    implicitWidth: 24; implicitHeight: 160
    activeFocusOnTab: true
    Accessible.role: Accessible.Slider
    Accessible.name: label
    Accessible.description: String(value)
    function apply(v) {
        var s = Math.max(from, Math.min(to, Math.round((v - from) / step) * step + from))
        s = Number(s.toFixed(decimals))
        if (s !== value) moved(s)
    }
    Rectangle { x: 9; y: 4; width: 6; height: parent.height - 8; radius: 3; color: T.ink_dark }
    Rectangle { x: 9; y: 4 + (parent.height - 8) * (1 - f.frac); width: 6; height: (parent.height - 8) * f.frac; radius: 3; color: Qt.alpha(f.tint, 0.8) }
    Rectangle {
        x: 0; y: 4 + (parent.height - 8) * (1 - f.frac) - 6; width: 24; height: 12; radius: 3
        color: T.metal; border.color: T.metal_dark
        Rectangle { anchors.centerIn: parent; width: 16; height: 2; color: T.metal_dark }
    }
    Rectangle { anchors.fill: parent; anchors.margins: -2; radius: 6; color: "transparent"; border.width: 2; border.color: T.accent; visible: f.activeFocus }
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        function set(m) { f.forceActiveFocus(); f.apply(f.from + (1 - Math.max(0, Math.min(1, (m.y - 4) / (height - 8)))) * (f.to - f.from)) }
        onPressed: function (m) { set(m) }
        onPositionChanged: function (m) { if (pressed) set(m) }
        preventStealing: true
        onWheel: function (w) { f.apply(f.value + (w.angleDelta.y > 0 ? 1 : -1) * f.step); w.accepted = true }
    }
    Keys.onPressed: function (e) {
        var d = { [Qt.Key_Left]: -1, [Qt.Key_Down]: -1, [Qt.Key_Right]: 1, [Qt.Key_Up]: 1, [Qt.Key_PageUp]: 10, [Qt.Key_PageDown]: -10 }[e.key]
        if (d !== undefined) f.apply(f.value + d * f.step)
        else if (e.key === Qt.Key_Home) f.apply(f.from)
        else if (e.key === Qt.Key_End) f.apply(f.to)
        else return
        e.accepted = true
    }
}
