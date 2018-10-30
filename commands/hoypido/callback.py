from commands.hoypido.utils import prettify_food_offers


def hoypido_callback(week_menu, requested_day):
    """Filter the menu for the requested day from the week_menu"""
    return prettify_food_offers(week_menu, int(requested_day))
