import os
import importlib
from rich import print

items = {}
item_mods = []


async def import_items() -> None:
    """
    Imports all items in the items folder and adds them to the items dict.
    """
    for file in sorted(os.listdir('items')):
        if file.endswith('.py') and not file.startswith('_'):
            item_name = file[:-3]
            mod = importlib.import_module(f'items.{item_name}')
            item_mods.append(mod)
            items[item_name] = mod.metadata

            print(
                f'Loaded item: [b white]{mod.metadata["item_name"]}[/b white]')


async def reload_items() -> None:
    """
    Refreshes the items dict.
    Since the item metadata is pulled from the database within each file, this allows
    for hotswapping of items and item metadata.
    """
    global items
    items = {}
    for mod in item_mods:
        importlib.reload(mod)
        items[mod.metadata['item_name']] = mod.metadata


async def fetch_item_by_name(name: str) -> dict:
    """
    Returns the item metadata for the given item name.
    Also accepts aliases.
    """
    for item in items.values():
        if name.lower() in item['aliases']:
            return item

    raise ValueError(f'Item not found: {name}')


def fetch_item_by_name_sync(name: str) -> dict:
    """
    Returns the item metadata for the given item name.
    Also accepts aliases.
    This is the synchronous version of fetch_item_by_name()
    """
    for item in items.values():
        if name.lower() in item['aliases']:
            return item

    raise ValueError(f'Item not found: {name}')


def item_search(query: str) -> list:
    """
    Returns a list of items that match the given query.
    Specifically used for Discord autocomplete.
    """
    results = []
    for item in items.values():
        if query.lower() in item['item_name'].lower() or any([query.lower() in alias.lower() for alias in item['aliases']]):
            results.append(item)
    return results
