selected_country = "Indian"  # Default value

def set_selected_country(country):
    """Update the selected country dynamically."""
    global selected_country
    selected_country = country

def get_selected_country():
    """Retrieve the currently selected country."""
    return selected_country
