import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Shapes

Rectangle {
    id: sg
    signal opened()
    property int focusSlot: 0
    property string query: ""
    readonly property string empty: "It's GP-200JR"
    radius: T.r_plate
    color: T.plate
    border.color: T.plate_border

    ListModel { id: banks }
    Component.onCompleted: { for (var i = 0; i < 85; i++) banks.append({ n0: "", n1: "", n2: "" }) }
    Connections {
        target: pedal
        function onSlot_name(slot, name) { banks.setProperty(Math.floor(slot / 3), "n" + (slot % 3), name) }
    }
    function open(s) { focusSlot = s; board.openSlot(s); sg.opened() }

    ColumnLayout {
        anchors { fill: parent; margins: T.s2 }
        spacing: T.s2
        RowLayout {
            spacing: T.s2
            TextField {
                id: search
                Layout.fillWidth: true; Layout.preferredHeight: 32
                placeholderText: "Buscar slot o nombre"
                leftPadding: 36; font.pixelSize: T.font_body; font.family: T.font; color: T.text
                placeholderTextColor: T.ink_soft
                Accessible.name: "Buscar slot"
                background: Rectangle { radius: 16; color: T.field_bg; border.color: T.field_border }
                Text { x: 12; anchors.verticalCenter: parent.verticalCenter; text: T.glyphs.search; font.family: T.icon_font; font.pixelSize: 16; color: T.dim }
                onTextChanged: sg.query = text
                Keys.onEscapePressed: text = ""
            }
            Btn { glyph: T.glyphs.reload; tip: "Releer la pedalera"; onClicked: board.rescan() }
        }
        ListView {
            id: list
            Layout.fillWidth: true; Layout.fillHeight: true
            clip: true
            model: banks
            focus: true
            activeFocusOnTab: true
            ScrollBar.vertical: ScrollBar { }
            Text { visible: list.contentHeight < 1; anchors.horizontalCenter: parent.horizontalCenter; y: 24; text: "Ningún slot coincide"; color: T.dim; font.family: T.font; font.pixelSize: T.font_body }
            Keys.onPressed: function (e) {
                var s = sg.focusSlot, b = Math.floor(s / 3), c = s % 3
                function shown(i) { return list.itemAtIndex(i) === null || list.itemAtIndex(i).shown }
                if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter || e.key === Qt.Key_Space) { sg.open(s); e.accepted = true; return }
                if (e.key === Qt.Key_Left) c = Math.max(0, c - 1)
                else if (e.key === Qt.Key_Right) c = Math.min(2, c + 1)
                else if (e.key === Qt.Key_Up || e.key === Qt.Key_Down) {
                    var d = e.key === Qt.Key_Up ? -1 : 1, nb = b + d
                    while (nb >= 0 && nb < 85 && !shown(nb)) nb += d
                    if (nb >= 0 && nb < 85) b = nb
                } else return
                sg.focusSlot = b * 3 + c
                list.positionViewAtIndex(b, ListView.Contain)
                e.accepted = true
            }
            delegate: Item {
                id: row
                required property int index
                required property string n0
                required property string n1
                required property string n2
                readonly property bool shown: [0, 1, 2].some(function (c) { return !!board && board.matches(String(index + 1) + "ABC"[c], [n0, n1, n2][c], sg.query) })
                width: list.width; height: shown ? 56 : 0; visible: shown
                Text { x: 0; width: 24; height: 52; text: row.index + 1; color: T.dim; font.pixelSize: T.font_small; font.family: T.font
                    horizontalAlignment: Text.AlignRight; verticalAlignment: Text.AlignVCenter }
                Repeater {
                    model: 3
                    Rectangle {
                        id: card
                        required property int index
                        readonly property int slot: row.index * 3 + index
                        readonly property string nm: [row.n0, row.n1, row.n2][index]
                        readonly property bool vacio: nm === sg.empty
                        readonly property bool cur: !!board && board.slot === slot
                        readonly property bool foc: list.activeFocus && sg.focusSlot === slot
                        x: 28 + index * ((row.width - 28 - 8) / 3 + 4); width: (row.width - 28 - 8) / 3; height: 52
                        radius: T.r_card
                        color: cur ? T.sel_fill : T.plate
                        border.width: foc ? 2 : 1
                        border.color: cur || foc ? T.accent : vacio ? "transparent" : T.sel_border
                        Accessible.role: Accessible.Button
                        Accessible.name: (row.index + 1) + "ABC"[index] + " " + (vacio ? "vacío" : nm)
                        Loader {
                            active: card.vacio && !card.cur && !card.foc
                            anchors.fill: parent
                            sourceComponent: Shape {
                                ShapePath { strokeColor: T.ink_off; strokeWidth: 1; strokeStyle: ShapePath.DashLine; dashPattern: [3, 3]; fillColor: "transparent"
                                    PathRectangle { x: 1; y: 1; width: card.width - 2; height: card.height - 2; radius: T.r_card } }
                            }
                        }
                        Text { x: 8; y: 4; text: (row.index + 1) + "ABC"[card.index]; color: card.vacio || card.nm === "" ? T.dim : T.text; font.bold: true; font.pixelSize: T.font_small; font.family: T.font }
                        Text { x: 8; y: 20; width: parent.width - 16; height: 28; wrapMode: Text.Wrap; maximumLineCount: 2; elide: Text.ElideRight
                            text: card.nm === "" ? "…" : card.vacio ? "vacío" : card.nm; font.pixelSize: T.font_small; font.family: T.font
                            color: card.vacio || card.nm === "" ? T.ink_soft : T.text }
                        Rectangle { visible: card.cur && board.dirty; x: parent.width - 12; y: 6; width: 6; height: 6; radius: 3; color: T.warn }
                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.LeftButton | Qt.RightButton
                            onClicked: function (m) { if (m.button === Qt.RightButton) cm.popup(); else { list.forceActiveFocus(); sg.open(card.slot) } }
                            Tip { text: (row.index + 1) + "ABC"[card.index] + " · " + (card.vacio ? "vacío" : card.nm || "…"); visible: parent.containsMouse }
                        }
                        Menu { id: cm; MenuItem { text: "Abrir"; onTriggered: sg.open(card.slot) } }
                    }
                }
            }
        }
        StatusPill { Layout.fillWidth: true; text: board ? board.scanStatus : ""; error: !!board && board.scanError }
    }
    Connections { target: board; function onStateChanged() { if (board.slot >= 0) sg.focusSlot = board.slot } }
}
