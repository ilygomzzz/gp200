import QtQuick
import QtQuick.Layouts

RowLayout {
    id: tb
    property int tab: 0
    property bool compact: false
    property bool chatDocked: true
    property bool chatRunning: false
    signal slotsClicked()
    signal chatClicked()
    spacing: T.s3
    Btn { visible: tb.compact; glyph: "\u{F035C}"; tip: "Slots (Ctrl+B)"; onClicked: tb.slotsClicked() }
    Text { text: T.glyphs.app; font.family: T.icon_font; font.pixelSize: 22; color: T.text }
    Text { text: "GP-200JR"; font.pixelSize: T.font_title; font.weight: Font.Medium; font.family: T.font; color: T.text }
    Rectangle {
        Layout.leftMargin: T.s3
        implicitWidth: 2 * 132; implicitHeight: 32; radius: 16; color: T.plate; border.color: T.plate_border
        Row {
            Repeater {
                model: ["Presets", "Chat general"]
                Rectangle {
                    required property int index
                    required property string modelData
                    width: 132; height: 32; radius: 16
                    color: tb.tab === index ? T.accent : "transparent"
                    Accessible.role: Accessible.PageTab; Accessible.name: modelData
                    Text { anchors.centerIn: parent; text: modelData; font.pixelSize: T.font_body; font.family: T.font; font.bold: tb.tab === index; color: tb.tab === index ? T.accent_text : T.dim }
                    MouseArea { anchors.fill: parent; onClicked: tb.tab = index }
                }
            }
        }
    }
    Item { Layout.fillWidth: true }
    Btn {
        visible: !tb.chatDocked && tb.tab === 0
        glyph: T.glyphs.chat; tip: "Chat (Ctrl+J)"; onClicked: tb.chatClicked()
        Rectangle { visible: tb.chatRunning; x: parent.width - 10; y: 2; width: 6; height: 6; radius: 3; color: T.accent }
    }
}
