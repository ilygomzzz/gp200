import QtQuick
import QtQuick.Effects

Item {
    id: led
    property bool on: false
    property color color: T.accent
    property real size: 8
    width: size; height: size
    Rectangle {
        id: dot
        anchors.fill: parent
        radius: width / 2
        color: led.on ? led.color : T.led_off
        border.width: led.on ? 0 : 1
        border.color: T.bevel_hi
        layer.enabled: T.fx && led.on
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: led.color; shadowBlur: 1.0; shadowOpacity: 0.9; shadowScale: 1.6 }
    }
}
