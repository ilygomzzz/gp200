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

    ColumnLayout {
        anchors { fill: parent; margins: 12 }
        spacing: 0
        Rectangle {
            id: face
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.maximumHeight: T.face_max_h; Layout.alignment: Qt.AlignTop
            radius: T.r_tile
            color: Qt.tint(T.chassis_base, Qt.alpha(cu.col, 0.6))
            opacity: board.loading ? 0.5 : 1
            enabled: !board.loading
            Rectangle {  // enamel: lit top, shaded bottom, 1 px highlight
                anchors.fill: parent; radius: parent.radius
                gradient: Gradient { GradientStop { position: 0; color: T.face_hi } GradientStop { position: 0.5; color: "transparent" } GradientStop { position: 1; color: T.face_lo } }
                Rectangle { x: parent.radius; y: 1; width: parent.width - 2 * parent.radius; height: 1; color: T.bevel_hi }
            }
            ColumnLayout {
                anchors { fill: parent; margins: T.s4 }
                spacing: T.s3
                ComboBox {
                    id: cb
                    Layout.preferredWidth: 480; Layout.maximumWidth: parent.width; Layout.preferredHeight: 60
                    editable: true
                    model: board.effects
                    Accessible.name: "Efecto"
                    leftPadding: 44; rightPadding: 40; topPadding: 0; bottomPadding: 24
                    function sync() { currentIndex = board.effects.indexOf(cu.unit ? cu.unit.effect : "") }
                    Component.onCompleted: sync()
                    Connections { target: board; function onChainChanged() { cb.sync() } function onEffectsChanged() { cb.sync() } }
                    onActivated: function (i) { board.setEffect(textAt(i)) }
                    onAccepted: { var i = find(editText, Qt.MatchContains); if (i >= 0) { currentIndex = i; board.setEffect(textAt(i)) } }
                    contentItem: TextField {
                        text: cb.editText
                        color: T.text; selectionColor: T.accent; selectedTextColor: T.accent_text
                        font.pixelSize: T.font_title; font.weight: Font.DemiBold; font.family: T.font
                        verticalAlignment: Text.AlignVCenter
                        background: null
                    }
                    indicator: Text { x: cb.width - 32; y: 18; text: "\u25be"; color: cu.col; font.pixelSize: T.font_title; font.family: T.font }
                    background: Rectangle {
                        radius: T.r_tile; color: T.nameplate
                        border.width: cb.activeFocus || cb.hovered ? 1 : 0; border.color: T.accent
                        Text { x: 12; y: 6; text: T.glyphs[board.selected] || ""; font.family: T.icon_font; font.pixelSize: 22; color: cu.col }
                        Text {
                            x: 44; y: 38; width: parent.width - 56
                            text: cu.unit ? (cu.unit.desc !== "" ? cu.unit.desc : "Efecto sin catálogo: solo se puede cambiar por otro") : ""
                            color: T.text; font.pixelSize: T.font_body; font.family: T.font; elide: Text.ElideRight
                        }
                    }
                    popup: Popup {
                        y: cb.height + 4; width: cb.width; height: Math.min(360, list.contentHeight + 2); padding: 1
                        contentItem: ListView { id: list; clip: true; model: cb.popup.visible ? cb.delegateModel : null; currentIndex: cb.highlightedIndex; ScrollBar.vertical: ScrollBar { } }
                        background: Rectangle { radius: T.r_tile; color: Qt.alpha(T.popup_bg, 1); border.color: T.sel_border }
                    }
                    delegate: ItemDelegate {
                        required property var modelData
                        required property int index
                        width: cb.width; height: 32
                        contentItem: Text { text: modelData; color: T.text; font.pixelSize: T.font_body; font.family: T.font; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                        background: Rectangle { color: cb.highlightedIndex === index ? T.sel_fill : "transparent" }
                    }
                }
                Text {
                    visible: board.selected === "DLY" && board.params.length > 0
                    text: board.dlyNote; color: T.warn; font.pixelSize: T.font_small; font.family: T.font
                    Layout.fillWidth: true; wrapMode: Text.WordWrap
                }
                Flickable {
                    id: fl
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 148  // knob row never clipped
                    contentHeight: body.height
                    interactive: contentHeight > height
                    clip: true
                    ScrollBar.vertical: ScrollBar { }
                    Column {
                        id: body
                        width: fl.width
                        spacing: pillsRow.height > 0 ? T.s3 : 0
                        Flow {
                            readonly property var knobs: board.params.filter(function (p) { return p.type === "knob" })
                            readonly property real dia: knobs.length > 8 ? T.knob_big : T.knob_face
                            width: Math.min(parent.width, knobs.length * (104 + T.s5) - T.s5)
                            x: (parent.width - width) / 2
                            spacing: T.s5
                            Repeater {
                                model: parent.knobs
                                Item {
                                    required property var modelData
                                    width: 104; height: 148
                                    Knob {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        dia: parent.parent.dia; onFace: true
                                        from: modelData.min; to: modelData.max; step: modelData.step
                                        value: board && board.values[modelData.name] !== undefined ? board.values[modelData.name] : modelData.default
                                        label: modelData.label; defaultValue: modelData.default
                                        arcColor: cu.col; locked: modelData.locked; lockTip: board ? board.dlyNote : ""
                                        onMoved: function (v) { board.setParam(modelData.name, v) }
                                    }
                                    Rectangle {  // label + value on a print chip: readable on any face
                                        x: (parent.width - width) / 2; y: 104; width: 72; height: 36; radius: 4; color: T.nameplate
                                        Column {
                                            anchors.centerIn: parent
                                            Text { width: 68; horizontalAlignment: Text.AlignHCenter; text: modelData.label; elide: Text.ElideRight
                                                color: T.dim; font.pixelSize: T.font_small; font.family: T.font }
                                            Text { width: 68; horizontalAlignment: Text.AlignHCenter; font.family: T.mono; font.pixelSize: T.font_small; color: T.text
                                                text: board && board.values[modelData.name] !== undefined ? Number(board.values[modelData.name]).toFixed(modelData.step >= 1 ? 0 : 2) : "" }
                                        }
                                    }
                                }
                            }
                        }
                        ParamPills { id: pillsRow; tint: cu.col }
                    }
                }
                Item {  // LED + footswitch bottom-centre, like the real pedal
                    Layout.alignment: Qt.AlignHCenter
                    implicitWidth: 56 + 100; implicitHeight: 78
                    Led { x: 23; y: 0; size: 10; on: cu.unit !== undefined && cu.unit.on; color: cu.col }
                    Footswitch { id: sw; y: 22; size: 56; on: cu.unit !== undefined && cu.unit.on; onClicked: board.toggle(board.selected) }
                    Rectangle {
                        x: 68; y: 39; width: lbl.implicitWidth + 16; height: 22; radius: 4; color: T.nameplate
                        Text { id: lbl; anchors.centerIn: parent; text: sw.on ? "Encendido" : "Apagado"; color: T.text; font.pixelSize: T.font_small; font.family: T.font }
                    }
                }
            }
        }
    }
}
