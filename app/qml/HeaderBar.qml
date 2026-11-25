import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: hb
    property bool narrow: false
    signal saveAsClicked()
    spacing: T.s3
    Rectangle {
        implicitWidth: pillText.implicitWidth + 24; implicitHeight: 32; radius: T.r_pill; color: T.accent_deep
        Text { id: pillText; anchors.centerIn: parent; text: board.slotLabel; color: T.accent_text; font.bold: true; font.pixelSize: T.font_body; font.family: T.font }
    }
    TextField {
        id: title
        Layout.fillWidth: true; Layout.minimumWidth: 120; Layout.preferredHeight: 44
        text: board.name
        enabled: board.busy === ""
        maximumLength: 16
        font.pixelSize: T.font_display; font.bold: true; font.family: T.font
        color: T.text
        selectByMouse: true
        Accessible.name: "Nombre del preset"
        background: Rectangle { radius: T.r_tile; color: title.activeFocus || title.hovered ? T.field_bg : "transparent"
            border.color: title.activeFocus || title.hovered ? T.field_border : "transparent" }
        onEditingFinished: { if (text !== board.name && !board.rename(text)) text = board.name }
    }
    Text {
        visible: board.dirty
        text: hb.narrow ? "●" : "● Sin guardar"
        color: T.warn; font.bold: true; font.pixelSize: T.font_body; font.family: T.font
        Tip { text: "Sin guardar"; visible: hb.narrow && chipHover.hovered }
        HoverHandler { id: chipHover }
    }
    Text {
        visible: board.factory
        text: "Preset de fábrica: guárdalo en un slot libre"
        color: T.warn; font.pixelSize: T.font_small; font.family: T.font
    }
    Btn { text: "Descartar"; enabled: board.dirty && board.busy === ""; onClicked: board.discard() }
    Btn { text: "Guardar en…"; enabled: board.dirty && board.busy === ""; onClicked: hb.saveAsClicked() }
    Btn { text: "Guardar"; primary: true; enabled: board.dirty && board.busy === "" && !board.factory; onClicked: board.save() }
}
