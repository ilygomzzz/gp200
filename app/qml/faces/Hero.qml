import QtQuick
import ".."

// Close-up hero: the selected unit's rendered ortho photo above its controls (knob caps baked, pointers + LED + names live).
Item {
    id: h
    property string block: ""
    property var info: null
    readonly property var ru: info && R.units ? R.units[info.key] : undefined
    readonly property var hero: ru ? ru.hero : undefined
    readonly property var size: hero ? hero.size : undefined
    readonly property real k: size ? Math.min(height / size[1], width / size[0], 1.6) : 1
    readonly property bool on: info !== null && info.on
    // treadles: rocker frame by value
    readonly property string img: hero && hero.frames ? hero.frames[Math.max(0, Math.min(hero.frames.length - 1, Math.round((info && info.knobs && info.knobs.length ? info.knobs[0] : 0.5) * (hero.frames.length - 1))))] : (hero ? hero.img : "")
    visible: size !== undefined
    Item {
        width: h.size ? h.size[0] : 0; height: h.size ? h.size[1] : 0; scale: h.k; transformOrigin: Item.TopLeft
        x: h.size ? (h.width - width * h.k) / 2 : 0; y: h.size ? (h.height - height * h.k) / 2 : 0
        Image { source: h.img !== "" ? T.render_dir + h.img : ""; width: h.size ? h.size[0] : 0; height: h.size ? h.size[1] : 0; smooth: true; mipmap: true }
        Repeater { model: h.hero ? h.hero.leds || [] : []; Image { required property var modelData; visible: h.on; source: T.render_dir + modelData.lit
            x: modelData.rect[0]; y: modelData.rect[1]; width: modelData.rect[2]; height: modelData.rect[3] } }
        Repeater { model: h.hero ? h.hero.knobs || [] : []; KnobSprite { required property var modelData; required property int index; markOnly: true
            type: modelData.type; cx: modelData.x; cy: modelData.y; r: modelData.r; sy: 1
            value: h.info && h.info.knobs.length > index ? h.info.knobs[index] : 0 } }
        Text {  // effect name in the label window (heads: light on dark; pedals: dark on the painted label)
            readonly property var nm: h.hero ? h.hero.name : undefined
            visible: nm !== undefined && h.info !== null
            text: h.info ? h.info.effect : ""
            x: nm ? nm[0] : 0; y: nm ? nm[1] : 0; width: nm ? nm[2] : 0; height: nm ? nm[3] : 0
            font.family: T.font; font.pixelSize: Math.max(8, height * 0.8); fontSizeMode: Text.Fit; minimumPixelSize: 6; font.bold: true; elide: Text.ElideRight
            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
            color: h.info && h.info.kind === "head" ? T.text : h.on ? T.ink_dark : T.ink_off; opacity: 0.9
        }
        Text {  // rack display
            readonly property var d: h.hero ? h.hero.display : undefined
            visible: d !== undefined && h.info !== null
            text: h.info ? h.info.effect : ""
            x: d ? d[0] + 4 : 0; y: d ? d[1] : 0; width: d ? d[2] - 8 : 0; height: d ? d[3] : 0
            font.family: T.font; font.pixelSize: Math.max(8, height * 0.7); elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter
            color: T.text; opacity: h.on ? 0.9 : 0.35
        }
    }
}
