
_STROKE = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'

# Each entry is the *inner* SVG markup only (no outer <svg> tag), in a
# 0 0 24 24 viewBox, drawn with simple primitives for a clean,
# consistent, professional look.
_ICONS: dict[str, str] = {
    "bag": '<path d="M6 8h12l-1 12.5a1.5 1.5 0 0 1-1.5 1.5h-7a1.5 1.5 0 0 1-1.5-1.5L6 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "target": '<circle cx="12" cy="12" r="7.5"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/>',
    "trending-up": '<polyline points="3.5,16 9.5,10 13.5,14 20.5,7"/><polyline points="14.5,7 20.5,7 20.5,13"/>',
    "trending-down": '<polyline points="3.5,8 9.5,14 13.5,10 20.5,17"/><polyline points="20.5,11 20.5,17 14.5,17"/>',
    "ruler": '<rect x="3.5" y="9" width="17" height="6" rx="1.2" transform="rotate(-8 12 12)"/><path d="M8 10.4 8.6 8.8M11.3 11 11.9 9.4M14.6 11.6 15.2 10" transform="rotate(-8 12 12)"/>',
    "layers": '<path d="M12 3.5 21 8l-9 4.5L3 8Z"/><path d="M3 12.5 12 17l9-4.5"/><path d="M3 16.5 12 21l9-4.5"/>',
    "tree": '<circle cx="12" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/><path d="M12 7v5M12 12 6 17M12 12l6 5"/>',
    "sparkle": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="M12 8 13.3 10.7 16 12 13.3 13.3 12 16 10.7 13.3 8 12 10.7 10.7Z"/>',
    "orb": '<circle cx="12" cy="11" r="6"/><path d="M9 20h6M12 17v3"/><path d="M9.5 9 10.6 11 12.6 11.6 10.6 12.2 9.5 14.2 8.4 12.2 6.4 11.6 8.4 11Z"/>',
    "brain": '<path d="M9.5 4.5a3 3 0 0 0-3 3v.3A3 3 0 0 0 5 13a3 3 0 0 0 1.6 5.4A2.7 2.7 0 0 0 9.5 21c1.4 0 2.5-1.1 2.5-2.5v-11c0-1.7-1.3-3-2.5-3Z"/><path d="M14.5 4.5a3 3 0 0 1 3 3v.3a3 3 0 0 1 1.5 5.2 3 3 0 0 1-1.6 5.4 2.7 2.7 0 0 1-2.9 2.6c-1.4 0-2.5-1.1-2.5-2.5v-11c0-1.7 1.3-3 2.5-3Z"/>',
    "bot": '<rect x="5" y="9" width="14" height="10" rx="3"/><path d="M12 9V6"/><circle cx="12" cy="4.5" r="1.3"/><circle cx="9" cy="14" r="1.1" fill="currentColor" stroke="none"/><circle cx="15" cy="14" r="1.1" fill="currentColor" stroke="none"/><path d="M2.5 13v3M21.5 13v3"/>',
    "bar-chart": '<path d="M4 20V10M12 20V4M20 20v-7"/><path d="M2.5 20h19"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 3.5v2.3M12 18.2v2.3M20.5 12h-2.3M5.8 12H3.5M17.8 6.2l-1.6 1.6M7.8 16.2l-1.6 1.6M17.8 17.8l-1.6-1.6M7.8 7.8 6.2 6.2"/>',
    "alert-triangle": '<path d="M12 4 2.5 20h19Z"/><path d="M12 10v4.5"/><circle cx="12" cy="17.3" r="0.6" fill="currentColor"/>',
    "cursor": '<path d="M6 3.5 18 12l-5.2 1.2L15 19l-2.6 1.2-2.4-6.1L6 17Z"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.6 3.1-6.5 7-6.5s7 2.9 7 6.5"/>',
    "rocket": '<path d="M12 3c2.8 1.5 4.5 4.6 4.5 8.3 0 2-.5 3.6-1.2 5l-3.3 3-3.3-3c-.7-1.4-1.2-3-1.2-5C7.5 7.6 9.2 4.5 12 3Z"/><circle cx="12" cy="10" r="1.6"/><path d="M8.5 15.5 6 18M15.5 15.5 18 18M9.5 19.5l1-2M14.5 19.5l-1-2"/>',
    "clipboard": '<rect x="5.5" y="5" width="13" height="16" rx="2"/><rect x="9" y="3" width="6" height="3.4" rx="1"/><path d="M8.5 11h7M8.5 14.5h7M8.5 18h4.5"/>',
    "repeat": '<path d="M4 7.5h11.5a3.5 3.5 0 0 1 3.5 3.5v1"/><path d="M6.5 5 4 7.5 6.5 10"/><path d="M20 16.5H8.5A3.5 3.5 0 0 1 5 13v-1"/><path d="M17.5 19 20 16.5 17.5 14"/>',
    "check-circle": '<circle cx="12" cy="12" r="8.5"/><path d="M8 12.3 10.8 15 16 9.3"/>',
    "scale": '<path d="M12 3v17M8 20h8"/><path d="M4 7.5h7.5M12.5 7.5H20"/><path d="M4 7.5 1.5 13a2.5 2.5 0 0 0 5 0L4 7.5Z"/><path d="M20 7.5 17.5 13a2.5 2.5 0 0 0 5 0L20 7.5Z"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5.2L15.3 14"/>',
    "trash": '<path d="M4.5 6.5h15"/><path d="M9 6.5V4.8a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1V6.5"/><path d="M6.5 6.5 7.3 19a1.6 1.6 0 0 0 1.6 1.5h6.2a1.6 1.6 0 0 0 1.6-1.5l.8-12.5"/><path d="M10 10.5v6M14 10.5v6"/>',
    "message": '<path d="M4 5.5h16v11H9.5L5 20v-3.5H4Z"/>',
    "paperclip": '<path d="M8 12.5 15.2 5.3a3 3 0 0 1 4.2 4.2L11 18a1.7 1.7 0 0 1-2.4-2.4l6.8-6.8"/>',
    "hand": '<path d="M8.5 12.5V6a1.5 1.5 0 0 1 3 0v5"/><path d="M11.5 11V4.5a1.5 1.5 0 0 1 3 0V11"/><path d="M14.5 11.2V6a1.5 1.5 0 0 1 3 0v8"/><path d="M8.5 11.5 6.8 10a1.6 1.6 0 0 0-2.3 2.2l4.4 5.3c1 1.3 2.6 2 4.3 2h1.6a5 5 0 0 0 5-5V9.8"/>',
    "receipt": '<path d="M6 3.5h12v17l-2-1.3-2 1.3-2-1.3-2 1.3-2-1.3-2 1.3Z"/><path d="M8.5 8h7M8.5 11.5h7M8.5 15h4.5"/>',
    "cart": '<circle cx="9.5" cy="19.5" r="1.3"/><circle cx="17" cy="19.5" r="1.3"/><path d="M3.5 4h2.3l2 12.2h10.9L20.5 8H7"/>',
    "dollar": '<circle cx="12" cy="12" r="8.5"/><path d="M12 6.5v11M14.8 9c0-1.1-1.2-2-2.8-2s-2.8.9-2.8 2 1.2 1.7 2.8 2 2.8.9 2.8 2-1.2 2-2.8 2-2.8-.9-2.8-2"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 9.5h17M8 3v3.5M16 3v3.5"/>',
    "users": '<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19c0-3.2 2.5-5.5 5.5-5.5s5.5 2.3 5.5 5.5"/><path d="M15.5 6.2A3 3 0 1 1 16.7 12"/><path d="M16 13.6c2.4.4 4 2.4 4 5.4"/>',
    "link": '<path d="M9.5 14.5 14.5 9.5"/><path d="M11 7.5 13 5.4a3.3 3.3 0 0 1 4.7 4.7L15.6 12"/><path d="M13 16.5l-2.1 2.1a3.3 3.3 0 0 1-4.7-4.7L8.4 12"/>',
    "grid": '<rect x="3.5" y="3.5" width="5.4" height="5.4" rx="1"/><rect x="15.1" y="3.5" width="5.4" height="5.4" rx="1"/><rect x="3.5" y="15.1" width="5.4" height="5.4" rx="1"/><rect x="15.1" y="15.1" width="5.4" height="5.4" rx="1"/><rect x="9.3" y="9.3" width="5.4" height="5.4" rx="1"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 20.5 20.5"/>',
    "book": '<path d="M12 6.5C10.5 5 8 4.5 4.5 4.8v13.7C8 18.2 10.5 18.7 12 20.2"/><path d="M12 6.5C13.5 5 16 4.5 19.5 4.8v13.7c-3.5-.3-6 .2-7.5 1.7Z"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5l-6 6a1.8 1.8 0 0 0 2.6 2.6l6-6a4 4 0 0 0 5-5.4l-2.9 2.9-2.5-.6-.6-2.5Z"/>',
    "layout": '<rect x="3.5" y="4" width="17" height="16" rx="2"/><path d="M3.5 9h17M9 9v11"/>',
    "database": '<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/><path d="M4.5 6v6c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8V6"/><path d="M4.5 12v6c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-6"/>',
    "monitor": '<rect x="3" y="4.5" width="18" height="12" rx="1.6"/><path d="M8.5 20h7M12 16.5V20"/>',
    "door": '<rect x="3.5" y="3" width="11" height="18" rx="1.4"/><path d="M14.5 12h6.2M18.4 8.5l2.3 3.5-2.3 3.5"/><circle cx="10.6" cy="12" r="0.7" fill="currentColor"/>',
    "arrow-right": '<path d="M4 12h16"/><path d="M14 6l6 6-6 6"/>',
    "arrow-up": '<path d="M12 20V4"/><path d="M6 10l6-6 6 6"/>',
    "info": '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5"/><circle cx="12" cy="7.8" r="0.7" fill="currentColor"/>',
    "flag": '<path d="M6 21V4"/><path d="M6 4h11l-2.5 3.5L17 11H6"/>',
}


def icon(name: str, size: int = 20, extra_class: str = "") -> str:
    """Return an inline <svg> string for `name` at `size` px.

    Falls back to a plain circle if the name isn't recognised, so a
    typo never breaks the page. Color is inherited from the parent via
    `currentColor` — style the wrapping element to recolor an icon.
    """
    body = _ICONS.get(name, '<circle cx="12" cy="12" r="8"/>')
    cls = f' class="ui-icon {extra_class}"'.rstrip() if extra_class else ' class="ui-icon"'
    return (
        f'<svg{cls} width="{size}" height="{size}" viewBox="0 0 24 24" {_STROKE}>'
        f"{body}</svg>"
    )
