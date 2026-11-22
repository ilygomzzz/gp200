import QtQuick
import QtQuick.Controls
import QtQuick.Shapes

FocusScope {
    id: k
    property real from: 0
    property real to: 100
    property real step: 1
    property real value: 0
    property real dia: T.knob_big
    property color arcColor: T.accent
    property bool locked: false
    property bool mini: false
    property string label: ""
    property real defaultValue: from
    property string lockTip: ""
    signal moved(real v)
    readonly property real pad: mini ? 0 : 16
    readonly property real frac: to > from ? Math.max(0, Math.min(1, (value - from) / (to - from))) : 0
    readonly property int decimals: step >= 1 ? 0 : 2
    readonly property real cx: width / 2
    readonly property real cy: height / 2
    readonly property real capR: dia * (mini ? 0.5 : 0.36)
    implicitWidth: dia + pad
    implicitHeight: dia + pad
    activeFocusOnTab: !mini && !locked
    Accessible.role: Accessible.Dial
    Accessible.name: label
    Accessible.description: String(value)

    function fmt(v) { return v.toFixed(decimals) }
    function apply(v) {
        var s = Math.max(from, Math.min(to, Math.round((v - from) / step) * step + from))
        s = Number(s.toFixed(decimals))
        if (s !== value) { moved(s); pop.name = label; pop.valueText = fmt(s); pop.open(); hide.restart() }
    }

    Shape {
        visible: !k.mini
        anchors.fill: parent
        ShapePath {
            strokeColor: T.ink_off; strokeWidth: 3; fillColor: "transparent"; capStyle: ShapePath.RoundCap
            PathAngleArc { centerX: k.cx; centerY: k.cy; radiusX: k.dia / 2 + 6; radiusY: k.dia / 2 + 6; startAngle: 135; sweepAngle: 270 }
        }
        ShapePath {
            strokeColor: k.locked ? "transparent" : k.arcColor; strokeWidth: 3; fillColor: "transparent"; capStyle: ShapePath.RoundCap
            PathAngleArc { centerX: k.cx; centerY: k.cy; radiusX: k.dia / 2 + 6; radiusY: k.dia / 2 + 6; startAngle: 135; sweepAngle: Math.max(0.01, 270 * k.frac) }
        }
    }
    Rectangle { visible: !k.mini; x: k.cx - k.dia / 2; y: k.cy - k.dia / 2; width: k.dia; height: k.dia; radius: k.dia / 2; color: T.knob_skirt }
    Shape {  // 48 knurl ticks = one dashed circle (dash lengths are in stroke widths)
        visible: !k.mini
        anchors.fill: parent
        ShapePath {
            strokeColor: T.knob_knurl; strokeWidth: 4; fillColor: "transparent"; strokeStyle: ShapePath.DashLine
            dashPattern: [0.25, Math.max(0.5, Math.PI * (k.dia - 4) / 48 / 4 - 0.25)]
            PathAngleArc { centerX: k.cx; centerY: k.cy; radiusX: k.dia / 2 - 2; radiusY: k.dia / 2 - 2; startAngle: 0; sweepAngle: 360 }
        }
    }
    Shape {
        anchors.fill: parent
        ShapePath {
            strokeColor: "transparent"; strokeWidth: 0
            fillGradient: RadialGradient {
                centerX: k.cx; centerY: k.cy; centerRadius: k.capR
                focalX: k.cx - k.capR * 0.3; focalY: k.cy - k.capR * 0.3
                GradientStop { position: 0; color: T.knob_cap_hi }
                GradientStop { position: 1; color: T.knob_cap }
            }
            PathAngleArc { centerX: k.cx; centerY: k.cy; radiusX: k.capR; radiusY: k.capR; startAngle: 0; sweepAngle: 360 }
        }
    }
    Item {  // pointer, rotated around the cap centre
        x: k.cx; y: k.cy; width: 0; height: 0
        rotation: -135 + 270 * k.frac
        visible: !k.locked
        Rectangle { x: -width / 2; y: -k.capR * 0.85; width: k.mini ? 1.5 : 2; height: k.capR * 0.55; radius: width / 2; color: T.text }
    }
    Text {
        visible: k.locked
        anchors.centerIn: parent
        text: T.glyphs.lock; font.family: T.icon_font; font.pixelSize: k.dia * 0.3; color: T.dim
    }
    Rectangle {
        visible: k.activeFocus && !k.mini
        x: k.cx - k.dia / 2 - 9; y: k.cy - k.dia / 2 - 9; width: k.dia + 18; height: k.dia + 18
        radius: width / 2; color: "transparent"; border.width: 2; border.color: T.accent
    }

    MouseArea {
        anchors.fill: parent
        enabled: !k.mini && !k.locked
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        property real y0: 0
        property real v0: 0
        onPressed: function (m) {
            k.forceActiveFocus()
            if (m.button === Qt.RightButton) { menu.popup(); return }
            y0 = m.y; v0 = k.value
        }
        onPositionChanged: function (m) {
            if (pressed && (pressedButtons & Qt.LeftButton))
                k.apply(v0 + (y0 - m.y) / 200 * (k.to - k.from) * ((m.modifiers & Qt.ShiftModifier) ? 0.2 : 1))
        }
        onWheel: function (w) { k.apply(k.value + (w.angleDelta.y > 0 ? 1 : -1) * k.step); w.accepted = true }
    }
    MouseArea { anchors.fill: parent; enabled: k.locked; hoverEnabled: true; id: lockArea }
    Tip { text: k.lockTip; visible: k.locked && k.lockTip !== "" && lockArea.containsMouse }
    Keys.onPressed: function (e) {
        if (k.locked || k.mini) return
        var d = { [Qt.Key_Left]: -1, [Qt.Key_Down]: -1, [Qt.Key_Right]: 1, [Qt.Key_Up]: 1, [Qt.Key_PageUp]: 10, [Qt.Key_PageDown]: -10 }[e.key]
        if (d !== undefined) k.apply(k.value + d * k.step)
        else if (e.key === Qt.Key_Home) k.apply(k.from)
        else if (e.key === Qt.Key_End) k.apply(k.to)
        else return
        e.accepted = true
    }
    Menu {
        id: menu
        MenuItem { text: "Escribir valor…"; onTriggered: { edit.text = k.fmt(k.value); edit.visible = true; edit.forceActiveFocus(); edit.selectAll() } }
        MenuItem { text: "Valor por defecto"; onTriggered: k.apply(k.defaultValue) }
    }
    TextField {
        id: edit
        visible: false
        anchors.centerIn: parent
        width: 72; height: 28
        horizontalAlignment: Text.AlignHCenter
        font.family: T.mono; font.pixelSize: T.font_small
        validator: DoubleValidator { bottom: k.from; top: k.to; decimals: k.decimals; notation: DoubleValidator.StandardNotation }
        background: Rectangle { color: T.popup_bg; radius: 8; border.color: T.accent }
        onAccepted: { k.apply(Number(text)); visible = false; k.forceActiveFocus() }
        Keys.onEscapePressed: { visible = false; k.forceActiveFocus() }
    }
    ValuePopup { id: pop; parent: k; x: (k.width - width) / 2; y: -height - 8 }
    Timer { id: hide; interval: 600; onTriggered: pop.close() }
}
