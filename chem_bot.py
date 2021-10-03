from os import getenv
import discord
import pubchempy as pcp
from discord.ext import commands
from collections import Counter


TOKEN = getenv('TOKEN')  # Change bot token
PREFIX = "chem "
client = commands.Bot(command_prefix = PREFIX, activity=discord.Game(name = PREFIX))


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
  smf = (" ".join(search_type_args.split()))
  found_cpmd = await search_mf(smf)

  if not found_cpmd:
    scm = search_type_args.split()
    found_cpmd = await search_name(scm)

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


client.run(TOKEN)
