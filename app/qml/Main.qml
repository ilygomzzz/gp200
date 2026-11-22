import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: win
    width: 1440; height: 900
    minimumWidth: 880; minimumHeight: 600
    visible: true
    title: "GP-200JR"
    color: T.glass ? "transparent" : T.bg
    readonly property bool wide: width >= T.w_wide
    readonly property bool slotsDocked: width >= T.w_medium
    readonly property bool compact: !slotsDocked
    readonly property int topH: 16 + 48
    palette {
        window: T.popup_bg; windowText: T.text; text: T.text; buttonText: T.text; button: T.sel_fill
        base: T.popup_bg; highlight: T.accent; highlightedText: T.accent_text; toolTipBase: T.popup_bg; toolTipText: T.text
        mid: T.sel_border; dark: T.sel_border; light: T.sel_fill; placeholderText: T.ink_soft
    }
    font { family: T.font; pixelSize: T.font_body }
    Overlay.modal: Rectangle { color: T.scrim }

    Rectangle { anchors.fill: parent; color: T.bg }
    Shortcut { sequence: "Ctrl+1"; onActivated: bar.tab = 0 }
    Shortcut { sequence: "Ctrl+2"; onActivated: bar.tab = 1 }
    Shortcut { sequence: "Ctrl+S"; onActivated: if (board.dirty && !board.factory && board.busy === "") board.save() }
    Shortcut { sequence: "Ctrl+B"; enabled: win.compact; onActivated: slotDrawer.opened ? slotDrawer.close() : slotDrawer.open() }
    Shortcut { sequence: "Ctrl+J"; enabled: !win.wide; onActivated: chatDrawer.opened ? chatDrawer.close() : chatDrawer.open() }
    onSlotsDockedChanged: if (slotsDocked) slotDrawer.close()
    onWideChanged: if (wide) chatDrawer.close()

    ColumnLayout {
        anchors { fill: parent; margins: T.s4 }
        spacing: T.s3
        TopBar {
            id: bar
            Layout.fillWidth: true; Layout.preferredHeight: 48
            compact: win.compact; chatDocked: win.wide; chatRunning: !!slotChat && slotChat.running
            onSlotsClicked: slotDrawer.open()
            onChatClicked: chatDrawer.open()
        }
        StackLayout {
            Layout.fillWidth: true; Layout.fillHeight: true
            currentIndex: bar.tab
            RowLayout {
                spacing: T.s3
                Item { id: leftDock; visible: win.slotsDocked; Layout.preferredWidth: 288; Layout.fillHeight: true }
                Flickable {
                    id: page
                    Layout.fillWidth: true; Layout.fillHeight: true
                    contentWidth: width; contentHeight: Math.max(height, col.implicitHeight)
                    clip: true; boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: ScrollBar { }
                    ColumnLayout {
                        id: col
                        width: page.width; height: page.contentHeight
                        spacing: T.s3
                        HeaderBar { visible: board.open; Layout.fillWidth: true; narrow: page.width < 960; onSaveAsClicked: saveAs.visible = true }
                        InlineBar {
                            visible: board.guard !== ""; Layout.fillWidth: true; text: "¿Descartar cambios de " + board.guard + "?"
                            Btn { text: "Descartar y cambiar"; onClicked: board.confirmSwitch() }
                            Btn { text: "Seguir editando"; onClicked: board.cancelSwitch() }
                            Item { Layout.fillWidth: true }
                        }
                        InlineBar {
                            id: saveAs
                            visible: false; Layout.fillWidth: true; text: "Guardar en"
                            ComboBox {
                                id: target
                                implicitWidth: 160; implicitHeight: 32
                                model: board.freeSlots.length ? board.freeSlots.map(function (f) { return f.label }) : ["No hay slots libres"]
                                background: Rectangle { radius: 16; color: T.field_bg; border.color: T.field_border }
                            }
                            Btn { text: "Guardar aquí"; enabled: board.freeSlots.length > 0; onClicked: { saveAs.visible = false; board.saveAs(board.freeSlots[target.currentIndex].slot) } }
                            Btn { text: "Cancelar"; onClicked: saveAs.visible = false }
                            Item { Layout.fillWidth: true }
                        }
                        Pedalboard {
                            id: pb
                            Layout.fillWidth: true
                            compactHint: win.compact
                            opacity: board.busy !== "" ? 0.5 : 1; enabled: board.busy === ""
                            onChooseSlot: slotDrawer.open()
                            onEditEffect: cu.focusPicker()
                        }
                        CloseUp {
                            id: cu
                            visible: board.open
                            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 260
                            opacity: board.busy !== "" ? 0.5 : 1; enabled: board.busy === ""
                        }
                        Item { visible: !board || !board.open; Layout.fillHeight: true }
                        StatusPill { Layout.fillWidth: true; text: board ? board.status : ""; error: !!board && board.statusError }
                    }
                }
                Item { id: rightDock; visible: win.wide; Layout.preferredWidth: 360; Layout.fillHeight: true }
            }
            ChatPane { view: globalChat }
        }
    }

    SlotGrid {
        parent: win.slotsDocked ? leftDock : slotDrawer.contentItem
        anchors.fill: parent
        onOpened: if (win.compact) slotDrawer.close()
    }
    ChatPane {
        id: slotPane
        view: slotChat
        parent: win.wide ? rightDock : chatDrawer.contentItem
        anchors.fill: parent
    }
    Drawer {
        id: slotDrawer
        edge: Qt.LeftEdge; y: win.topH; width: 312; height: win.height - y
        interactive: win.compact
        background: Rectangle { color: Qt.alpha(T.popup_bg, 1) }
    }
    Drawer {
        id: chatDrawer
        edge: Qt.RightEdge; y: win.topH; width: 380; height: win.height - y
        interactive: !win.wide
        background: Rectangle { color: Qt.alpha(T.popup_bg, 1) }
    }
}
