import QtQuick

// Contact shadow sprite under a unit (centre on its bottom edge); same with GP200_FX=0.
Image {
    property real wide: 100
    property real strength: T.tex_shadow
    source: T.tex_dir + "shadow_contact.png"
    width: wide * 1.15; height: 24
    opacity: strength
    smooth: true
}
