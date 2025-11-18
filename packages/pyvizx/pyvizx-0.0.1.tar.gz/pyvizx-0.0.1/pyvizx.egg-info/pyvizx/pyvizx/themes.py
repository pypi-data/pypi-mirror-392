THEMES = {
    "default": {
        "color": "#1f77b4",
        "title_size": 14,
        "label_size": 12
    },
    "tamil_theme": {
        "color": "#FFB300",   # yellow-orange
        "title_size": 16,
        "label_size": 13
    }
}

def get_theme(name="default"):
    return THEMES.get(name, THEMES["default"])
