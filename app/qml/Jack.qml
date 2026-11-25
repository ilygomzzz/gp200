import QtQuick

Item {
    property string label: ""
    width: 40; height: T.cell_h
    Rectangle { x: 0; y: 40; width: 40; height: 64; radius: 8; color: T.jack; border.color: T.metal_dark }
    Rectangle { x: 10; y: 62; width: 20; height: 20; radius: width / 2; color: T.cable; border.color: T.metal_dark }
    Text { y: 116; x: -20; width: 80; horizontalAlignment: Text.AlignHCenter; text: label; color: T.dim; font.pixelSize: T.font_small; font.family: T.font }
}
