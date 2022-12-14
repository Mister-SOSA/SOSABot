"""
This module just contains a function that checks if a user has permission to use a command.
"""

import db_manager as database
import discord

ranks = ['Member', 'Admin', 'SOSA']


def has_permission(user, metadata):
    user_permission = database.fetch_permission(user)[0]
    command_permission = metadata['permission_level']

    if ranks.index(user_permission) >= ranks.index(command_permission):
        return True
    else:
        return False
