import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: cu
    property alias picker: cb
    readonly property var unit: board.units[board.selected]
    readonly property color col: T.block_colors[board.selected] || T.dim
    radius: T.r_plate
    color: T.plate
    border.color: T.plate_border
    function focusPicker() { cb.forceActiveFocus(); cb.contentItem.selectAll() }

    Rectangle {
        id: face
        anchors { fill: parent; margins: 12 }
        radius: 16
        color: Qt.tint(T.chassis_base, Qt.alpha(cu.col, 0.6))
        opacity: board.loading ? 0.5 : 1
        enabled: !board.loading
        ColumnLayout {
            anchors { fill: parent; margins: T.s4 }
            spacing: T.s3
            RowLayout {
                spacing: T.s3
                Layout.fillWidth: true
                Rectangle {
                    width: 40; height: 40; radius: 20; color: Qt.alpha(T.ink_dark, 0.25)
                    Text { anchors.centerIn: parent; text: T.glyphs[board.selected] || ""; font.family: T.icon_font; font.pixelSize: 22; color: T.ink_dark }
                }
                ComboBox {
                    id: cb
                    Layout.minimumWidth: 240; Layout.preferredHeight: 36
                    editable: true
                    model: board.effects
                    Accessible.name: "Efecto"
                    function sync() { currentIndex = board.effects.indexOf(cu.unit ? cu.unit.effect : "") }
                    Component.onCompleted: sync()
                    Connections { target: board; function onChainChanged() { cb.sync() } function onEffectsChanged() { cb.sync() } }
                    onActivated: function (i) { board.setEffect(textAt(i)) }
                    onAccepted: { var i = find(editText, Qt.MatchContains); if (i >= 0) { currentIndex = i; board.setEffect(textAt(i)) } }
                    background: Rectangle { radius: 18; color: T.field_bg; border.color: T.field_border }
                }
                Text {
                    Layout.fillWidth: true
                    text: cu.unit ? (cu.unit.desc !== "" ? cu.unit.desc : "Efecto sin catálogo: solo se puede cambiar por otro") : ""
                    color: T.ink_dark; font.pixelSize: T.font_desc; font.family: T.font; elide: Text.ElideRight
                }
                Led { size: 10; on: cu.unit !== undefined && cu.unit.on; color: cu.col; Layout.alignment: Qt.AlignVCenter }
                Footswitch { size: 56; on: cu.unit !== undefined && cu.unit.on; onClicked: board.toggle(board.selected) }
            }
            Text {
                visible: board.selected === "DLY" && board.params.length > 0
                text: board.dlyNote; color: T.warn; font.pixelSize: T.font_desc; font.family: T.font
                Layout.fillWidth: true; wrapMode: Text.WordWrap
            }
            Flickable {
                id: fl
                Layout.fillWidth: true; Layout.fillHeight: true
                contentHeight: body.height
                clip: true
                ScrollBar.vertical: ScrollBar { }
                Column {
                    id: body
                    width: fl.width
                    spacing: T.s3
                    Flow {
                        width: parent.width
                        spacing: T.s2
                        topPadding: 72  // room for the value popup bubble
                        Repeater {
                            model: board.params.filter(function (p) { return p.type === "knob" })
                            Item {
                                required property var modelData
                                width: 88; height: 112
                                Knob {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    from: modelData.min; to: modelData.max; step: modelData.step
                                    value: board && board.values[modelData.name] !== undefined ? board.values[modelData.name] : modelData.default
                                    label: modelData.label; defaultValue: modelData.default
                                    arcColor: cu.col; locked: modelData.locked; lockTip: board ? board.dlyNote : ""
                                    onMoved: function (v) { board.setParam(modelData.name, v) }
                                }
                                Text { y: 78; width: parent.width; horizontalAlignment: Text.AlignHCenter; text: modelData.label; elide: Text.ElideRight
                                    color: T.ink_dark; font.pixelSize: T.font_desc; font.family: T.font }
                                Text { y: 96; width: parent.width; horizontalAlignment: Text.AlignHCenter; font.family: T.mono; font.pixelSize: T.font_small; color: T.ink_dark
                                    text: board && board.values[modelData.name] !== undefined ? Number(board.values[modelData.name]).toFixed(modelData.step >= 1 ? 0 : 2) : "" }
                            }
                        }
                    }
                    ParamPills { tint: cu.col }
                }
            }
        }
    }
}
