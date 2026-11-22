import QtQuick
import QtQuick.Controls

Flow {
    id: pills
    property color tint: T.accent
    spacing: T.s2
    Repeater {
        model: board.params.filter(function (p) { return p.type !== "knob" })
        Loader {
            required property var modelData
            sourceComponent: modelData.options.length > 2 || modelData.type === "combox" ? combo : toggle
            Component {
                id: combo
                ComboBox {
                    height: 32
                    model: modelData.options.map(function (o) { return modelData.label + ": " + o.name })
                    currentIndex: modelData.options.findIndex(function (o) { return o.id === board.values[modelData.name] })
                    onActivated: function (i) { board.setParam(modelData.name, modelData.options[i].id) }
                    background: Rectangle { radius: 16; color: T.field_bg; border.color: T.field_border }
                    Accessible.name: modelData.label
                }
            }
            Component {
                id: toggle
                Btn {
                    text: modelData.label; checkable: true
                    checked: board.values[modelData.name] === 1
                    onClicked: board.setParam(modelData.name, checked ? 1 : 0)
                    background: Rectangle { radius: 16; color: parent.checked ? Qt.alpha(pills.tint, 0.25) : "transparent"
                        border.color: parent.checked ? pills.tint : T.sel_border }
                }
            }
        }
    }
}
