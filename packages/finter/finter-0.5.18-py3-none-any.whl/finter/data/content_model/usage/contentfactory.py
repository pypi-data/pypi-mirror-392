"""
ContentFactory usage documentation.
"""

CONTENTFACTORY_GENERAL_USAGE_TEXT = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     ContentFactory Usage Guide                             ║
╚════════════════════════════════════════════════════════════════════════════╝

📖 Basic Usage:
   cf = ContentFactory(universe_name, start, end)
   df = cf.get_df(item_name, **kwargs)

💡 Common Parameters:
   - item_name: Item to retrieve (see cf.item_list for all items)

📋 Available Methods:
   - cf.show()              : Interactive item explorer
   - cf.item_list           : List all available items
   - cf.search(query)       : Search for items
   - cf.summary()           : Show category summary
   - cf.usage(item_name)    : Show item-specific usage (if available)

For item-specific parameters,
use: cf.usage(item_name)
"""


def get_standard_item_usage(item_name):
    """Returns standard usage text for items without special features."""
    return f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                     Usage for: {item_name:<53}                             ║
╚════════════════════════════════════════════════════════════════════════════╝

📖 Basic Usage:
   df = cf.get_df('{item_name}')

💡 This item uses the standard get_df interface.

📌 Common Parameters:
   - fill_nan (default: True)
     * True: Prevents lookahead bias by not showing last day data
     * False: Shows all data including last day
     Example: df = cf.get_df('{item_name}', fill_nan=False)
"""
