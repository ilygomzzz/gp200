import QtQuick

// A rendered unit: baked sprite (shadows included), lit LED patches, live knob marks, name in perspective. Coordinates: stage units,
// relative to the unit's own rect origin (`u.rect`).
Item {
    id: ru
    property var u: ({})
    property var info: null
    property bool on: false
    property bool labels: true
    readonly property var r0: u.rect || [0, 0, 0, 0]
    readonly property var nm: u.name
    // treadles: pick the pre-rendered rocker frame by value (0..1)
    readonly property var fr: u.frames && u.frames.length ? u.frames[Math.max(0, Math.min(u.frames.length - 1, Math.round(((info && info.knobs && info.knobs.length ? info.knobs[0] : 0.5)) * (u.frames.length - 1))))] : u
    Image {
        source: T.render_dir + ru.fr.img; smooth: true
        x: ru.fr.img_rect[0] - ru.r0[0]; y: ru.fr.img_rect[1] - ru.r0[1]; width: ru.fr.img_rect[2]; height: ru.fr.img_rect[3]
    }
    Repeater {
        model: ru.u.leds || []
        Image {
            required property var modelData
            visible: ru.on; source: T.render_dir + modelData.lit; smooth: true
            x: modelData.rect[0] - ru.r0[0]; y: modelData.rect[1] - ru.r0[1]; width: modelData.rect[2]; height: modelData.rect[3]
        }
    }
    Repeater {
        model: ru.u.knobs || []
        KnobSprite {
            required property var modelData
            required property int index
            markOnly: true; type: modelData.type; cx: modelData.x - ru.r0[0]; cy: modelData.y - ru.r0[1]; r: modelData.r; sy: modelData.sy
            value: ru.info && ru.info.knobs.length > index ? ru.info.knobs[index] : 0
        }
    }
    Text {
        visible: ru.labels && ru.nm !== undefined && ru.info !== null && ru.info.kind !== "stompbox" && ru.info.kind !== "mini" && ru.info.kind !== "eq"  // pedal names live in chips/close-up: the label window sits under the knob row
        text: ru.info ? ru.info.effect : ""
        x: ru.nm ? ru.nm[0] - ru.r0[0] : 0; y: ru.nm ? ru.nm[1] - ru.r0[1] : 0; width: ru.nm ? ru.nm[2] : 0; height: ru.nm ? ru.nm[3] : 0
        font.family: T.font; font.pixelSize: Math.max(8, height * 0.8); font.bold: true; elide: Text.ElideRight
        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
        color: ru.u.img.indexOf("AMP_") === 0 ? T.text : ru.on ? T.ink_dark : T.ink_off; opacity: 0.85
        transform: Scale { yScale: ru.nm ? Math.max(0.35, Math.min(1, ru.nm[4])) : 1; origin.y: height / 2 }
    }
    Text {  // rack units: live readout in the rendered display window
        readonly property var d: ru.u.display
        visible: ru.labels && d !== undefined && ru.info !== null
        text: ru.info ? ru.info.effect : ""
        x: d ? d[0] - ru.r0[0] : 0; y: d ? d[1] - ru.r0[1] : 0; width: d ? d[2] : 0; height: d ? d[3] : 0
        font.family: T.font; font.pixelSize: Math.max(7, height * 0.7); elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter
        color: T.text; opacity: ru.on ? 0.9 : 0.35
    }
}
