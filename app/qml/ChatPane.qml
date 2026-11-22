import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: cp
    required property var view
    radius: T.r_plate
    color: T.plate
    border.color: T.plate_border
    ColumnLayout {
        anchors { fill: parent; margins: T.s3 }
        spacing: T.s2
        RowLayout {
            Text { Layout.fillWidth: true; text: cp.view ? cp.view.title : ""; elide: Text.ElideRight; color: T.text; font.bold: true; font.pixelSize: T.font_body; font.family: T.font }
            Btn { glyph: T.glyphs.new_chat; tip: "Nueva conversación"; enabled: !!cp.view && cp.view.bound && cp.view.locked === ""; onClicked: cp.view.reset() }
        }
        Flickable {
            id: fl
            Layout.fillWidth: true; Layout.fillHeight: true
            clip: true
            contentHeight: log.height
            ScrollBar.vertical: ScrollBar { }
            TextArea {
                id: log
                width: fl.width
                readOnly: true
                textFormat: TextEdit.RichText
                wrapMode: TextEdit.Wrap
                text: cp.view ? cp.view.html : ""
                color: T.text; font.pixelSize: T.font_desc; font.family: T.font
                background: null
                Accessible.name: "Conversación"
                onTextChanged: Qt.callLater(function () { fl.contentY = Math.max(0, fl.contentHeight - fl.height) })
                onLinkActivated: function (l) { Qt.openUrlExternally(l) }
            }
        }
        Text { Layout.fillWidth: true; visible: text !== ""; text: cp.view ? cp.view.hint : ""; wrapMode: Text.WordWrap; color: T.dim; font.pixelSize: T.font_desc; font.family: T.font }
        TextField {
            id: input
            Layout.fillWidth: true; Layout.preferredHeight: 40
            enabled: !!cp.view && cp.view.bound && cp.view.locked === ""
            placeholderText: cp.view && cp.view.bound ? (cp.view.locked !== "" ? cp.view.locked : cp.view.placeholder) : ""
            placeholderTextColor: T.ink_soft
            color: T.text; font.pixelSize: T.font_body; font.family: T.font
            rightPadding: 44; leftPadding: 16
            Accessible.name: "Mensaje para Claude"
            background: Rectangle { radius: 20; color: T.field_bg; border.color: T.field_border }
            onAccepted: send()
            function send() { if (text.trim() !== "") { cp.view.send(text); text = "" } }
            Btn { glyph: T.glyphs.send; tip: "Enviar (Enter)"; enabled: input.enabled; anchors { right: parent.right; rightMargin: 4; verticalCenter: parent.verticalCenter }
                onClicked: input.send() }
        }
    }
}
