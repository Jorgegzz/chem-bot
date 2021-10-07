from os import getenv
import discord
import pubchempy as pcp
import eq_balancer as eb
from discord.ext import commands
from collections import Counter


TOKEN = getenv('TOKEN')
PREFIX = "totno "
client = commands.Bot(command_prefix = PREFIX, activity = discord.Game(name = PREFIX))
client.remove_command("help")


@client.event
async def on_ready():
    print("Bot has successfully logged in as: {}".format(client.user))
    print("Bot ID: {}\n".format(client.user.id))


#@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            embed=discord.Embed(
                description=f'**Command not found!**',
                color=discord.Color.red()),
        )
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(
            embed=discord.Embed(
                description='**Compound not found!**',
                color=discord.Color.red()),
        )


# Help Command #
@client.command()
async def help(ctx):
    embed = discord.Embed(
        title = "List of commands",
        color = discord.Color.green()
    )
    embed.add_field(
        name="chem search ( compound name or formula )",
        value="Returns compound info",
        inline=False
    )
    embed.add_field(
        name="chem balance ( chemical equation Ex. *C + H3O = CO2 + H*  )",
        value="Returns balanced equation (Verifies individual"
              " compounds but doesnt verify if the reaction itself is possible)\n",
        inline=False
    )
    embed.set_footer(
        text = "Warning: this bot is still being developed and you may encounter errors"
    )
    emoji = "\u2705"
    await ctx.message.add_reaction(emoji)
    await ctx.author.send(embed=embed)


# Search Equations #
async def search_mf(name_name):
    name_results = pcp.get_compounds(name_name, "name")
    if bool(name_results):
        return name_results[0]
    else:
        return False


async def search_name(name_mf):
    keys = []
    mf_results = pcp.get_compounds(name_mf, "formula")

    for c in mf_results:
        keys.append(c.cid)

    r_cid = sorted(keys)[0]
    result_compound = pcp.Compound.from_cid(r_cid)
    return result_compound


@client.command()
async def search(ctx, *, search_type_args):
    async with ctx.typing():
        scm = (" ".join(search_type_args.split()))
        found_cpmd = await search_mf(scm)

        if not found_cpmd:
            smf = search_type_args.split()
            found_cpmd = await search_name(smf)

    embed = discord.Embed(
        title=found_cpmd.synonyms[0],
        url=f"https://pubchem.ncbi.nlm.nih.gov/compound/{found_cpmd.cid}",
        color=discord.Color.green()
    )

    embed.set_author(
        name=f"Requested by {ctx.author.display_name}",
        icon_url=ctx.author.avatar_url
    )

    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    embed.add_field(
        name="**Molecular Formula**",
        value=f"{found_cpmd.molecular_formula.translate(SUB)}",
        inline=True
    )

    embed.add_field(
        name="**Molecular Weight**",
        value=f"{found_cpmd.molecular_weight}",
        inline=True
    )

    ind_elements = ""

    for key, value in Counter(found_cpmd.elements).items():
        ind_elements += f"**{key}** : {value}\n"

    embed.add_field(
        name="**Element Count**",
        value=f"{ind_elements}",
        inline=True
    )

    embed.add_field(
        name="**IUPAC name**",
        value=f"{found_cpmd.iupac_name}",
        inline=True
    )

    other_names = ""
    for synonym in found_cpmd.synonyms[1:4]:
        other_names += f"{synonym}\n"

    embed.add_field(
        name="**Other names**",
        value=f"{other_names}",
        inline=False
    )

    embed.set_thumbnail(
        url=f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={found_cpmd.cid}&t=l"
    )

    embed.set_footer(
        text="Retrieved from pubchem using the pubchempy library"
    )

    await ctx.send(embed=embed)


# Balance Equations #
async def get_comp_link(reac_prod):
    splt = reac_prod.split("+")
    output_comp = ""
    for ind, comp in enumerate(splt):
        found_comp = await search_name(comp)
        reac_link = f"[{comp}](https://pubchem.ncbi.nlm.nih.gov/compound/{found_comp.cid})"
        if ind != 0:
            output_comp += f"+ {reac_link}"
        else:
            output_comp += reac_link
    return output_comp


@client.command()
async def balance(ctx, *, equation):
    split_equation = equation.split("=", 1)
    reactants = split_equation[0]
    products = split_equation[1]

    async with ctx.typing():
        embed = discord.Embed(
            title = "Balance Equation",
            color = discord.Color.blue()
        )

        embed.set_author(
            name=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url
        )

        embed.add_field(
            name="**Reactants**",
            value = await get_comp_link(reactants),
            inline = True
        )

        embed.add_field(
            name="**Products**",
            value = await get_comp_link(products),
            inline = True
        )

        embed.add_field(
            name="**Balanced**",
            value = f"{eb.balance(reactants, products)}".replace("**1**", ""),
            inline = False
        )
    await ctx.send(embed=embed)


client.run(TOKEN)
