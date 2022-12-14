"""
A helper module for generating help embeds (specifically for prefix commands)
"""

import discord


def generate_help_embed(client, metadata, has_permission=True, command_disabled=False):
    helper_embed = discord.Embed(
        title=f'{metadata["emoji"]} {metadata["name"]}',
        description=f'{metadata["description"]}',
        color=0x00ff00
    ).add_field(
        name='Aliases',
        value='\n'.join(f'`!{alias}`' for alias in metadata['aliases']),
        inline=False
    ).add_field(
        name='Syntax',
        value=f'`{metadata["syntax"]}`',
        inline=False
    )

    if metadata['subcommands']:
        helper_embed.add_field(
            name='Subcommands',
            value='\n'.join(
                f'`{subcommand}`' for subcommand in metadata['subcommands']),
            inline=False
        )

    if metadata['usage_examples']:
        helper_embed.add_field(
            name='Usage Examples',
            value='\n'.join(
                f'`{example}`' for example in metadata['usage_examples']),
            inline=False
        )

    helper_embed.add_field(
        name='Permission Level',
        value=f'`{metadata["permission_level"]}`',
        inline=False
    )

    if not has_permission:
        helper_embed.set_footer(
            text='🚫 You do not have permission to use this command.')

    if command_disabled:
        helper_embed.set_footer(
            text='🚫 This command is currently disabled.')

    return helper_embed
