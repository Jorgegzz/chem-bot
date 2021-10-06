from os import getenv
import discord
import pubchempy as pcp
import eq_balancer as eb
from discord.ext import commands
from collections import Counter


TOKEN = "TOKEN"  # Change bot token
PREFIX = "totno "
client = commands.Bot(command_prefix = PREFIX, activity = discord.Game(name = PREFIX))


@client.event
async def on_ready():
    print("Bot has successfully logged in as: {}".format(client.user))
    print("Bot ID: {}\n".format(client.user.id))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            embed=discord.Embed(
                description=f'**Command not found!.**',
                color=discord.Color.red()),
            delete_after=5.0
        )


# Search #
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


@client.command()
async def balance(ctx, *, equation):
    split_equation = equation.split("=", 1)
    reactants = split_equation[0]
    products = split_equation[1]

    await ctx.send("Loading (This may take a while)...")
    embed = discord.Embed(
        title = "Balance Equation",
        color = discord.Color.blue()
    )

    embed.set_author(
        name=f"Requested by {ctx.author.display_name}",
        icon_url=ctx.author.avatar_url
    )
    splt_reactants = products.split("+")
    output_reacs = ""
    for ind, reac in enumerate(splt_reactants):
        found_reac = await search_name(reac)
        reac_link = f"[{reac}](https://pubchem.ncbi.nlm.nih.gov/compound/{found_reac.cid})"
        if ind != 0:
            output_reacs += f"+ {reac_link}"
        else:
            output_reacs += reac_link
    embed.add_field(
        name="**Reactants**",
        value = output_reacs,
        inline = True
    )

    splt_products = products.split("+")
    output_prods = ""
    for ind, prod in enumerate(splt_products):
        found_prod = await search_name(prod)
        prod_link = f"[{prod}](https://pubchem.ncbi.nlm.nih.gov/compound/{found_prod.cid})"
        if ind != 0:
            output_prods += f" + {prod_link}"
        else:
            output_prods += prod_link

    embed.add_field(
        name="**Products**",
        value = output_prods,
        inline = True
    )

    embed.add_field(
        name="**Balanced**",
        value = f"{eb.balance(reactants, products)}".replace("**1**", ""),
        inline = False
    )
    await ctx.send(embed=embed)


client.run(TOKEN)
