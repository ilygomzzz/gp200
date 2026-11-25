import QtQuick

// Colourless alpha material tile (tools/make_textures.py) over whatever colour is under it; inset so it stays inside round corners.
Item {
    property string src: ""
    property real op: 0.3
    property real inset: 0
    anchors.fill: parent
    anchors.margins: inset
    clip: true
    Image { anchors.fill: parent; source: T.tex_dir + src + ".png"; fillMode: Image.Tile; smooth: true; opacity: parent.op }
}
