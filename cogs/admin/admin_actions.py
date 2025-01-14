import discord
import os
import subprocess

from discord_slash.utils.manage_commands import create_choice

from base_logger import logger
from discord.ext import commands
from config import TEST2_CHANNEL_ID, GENERAL_CHANNEL_ID, ROOT_DIR, COMMAND_PREFIX, ADMIN_ID, TEST_CHANNEL_ID
from utils import get_public_url, embed_send
from discord_slash import cog_ext, SlashContext, manage_commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Turns on/off my Master\'s PC')
    async def power(self, ctx, arg=None):
        await self._power(ctx, arg)

    @cog_ext.cog_slash(name="power",
                       description='Turns on/off my Master\'s PC',
                       #guild_ids=[207481917975560192, 572648167573684234],
                       options=[manage_commands.create_option(
                            name="arg",
                            description="\"on\" to switch on, \"off\" to switch off",
                            option_type=3,
                            required=True,
                            choices=[
                                   create_choice(
                                       name="On",
                                       value="on"
                                   ),
                                   create_choice(
                                       name="Off",
                                       value="off"
                                   )
                               ]
                            ),
                       ],
                       )
    async def powers(self, ctx: SlashContext, arg: str):
        await self._power(ctx, arg)

    async def _power(self, ctx, arg: str):
        logger.debug("PRE: {}".format(ctx))
        try:
            if not arg:
                if isinstance(ctx, discord.ext.commands.context.Context):
                    await ctx.send('```Usage:(ADMIN ONLY)\n'
                                   '{}power on : to switch on PC\n'
                                   '{}power off : to shutdown PC\n```'.format(COMMAND_PREFIX,
                                                                              COMMAND_PREFIX))

            elif arg.lower() == "on":
                if ctx.author.id == int(ADMIN_ID):
                    ''' api way '''
                    '''
                    session = aiohttp.ClientSession()
                    data = {"action": "on"}
                    api_path = os.path.join(ROOT_DIR, "keys/api")
                    try:
                        
                        # read API endpoint from file
                        # with open(api_path) as f:
                        #    pc_api = f.read().strip()
                        # res = await session.post(pc_api, data=json.dumps(data), headers={'content-type': 'application/json'})
                        # await session.close()
        
                        await ctx.send('```Done```')
                    except Exception as e:
                        logger.exception(e)
                    '''

                    ''' direct call '''
                    master_mac_path = os.path.join(ROOT_DIR, "keys/master_mac")
                    with open(master_mac_path) as f:
                        master_mac = f.read().strip()
                    logger.debug("Powering on PC")
                    os.system("wakeonlan {}".format(master_mac))
                    await ctx.send("```Powering on PC```")
                else:
                    await ctx.send("```Only my master can use this command```")

            elif arg.lower() == "off":
                admin_id_path = os.path.join(ROOT_DIR, "keys/admin_id")
                with open(admin_id_path) as f:
                    admin_id = f.read().strip()
                if ctx.author.id == int(admin_id):
                    master_ip_path = os.path.join(ROOT_DIR, "keys/master_ip")
                    with open(master_ip_path) as f:
                        master_ip = f.read().strip()
                    logger.debug("Shutting down PC")
                    os.system("ssh preetham@{} shutdown /s".format(master_ip))
                    await ctx.send('```Shutting down PC```')
                else:
                    await ctx.send('```Only my master can use this command.```')
            else:
                await ctx.send('```Invalid entry```')
                if isinstance(ctx, discord.ext.commands.context.Context):
                    await ctx.send('```Usage:(ADMIN ONLY)\n'
                                   '{}power on : to switch on PC\n'
                                   '{}power off : to shutdown PC\n```'.format(COMMAND_PREFIX,
                                                                              COMMAND_PREFIX))
        except Exception as e:
            logger.exception(e)
            await ctx.send('```Zzzzz```')

    @commands.command(brief='', hidden=True)
    async def post(self, ctx, *args):
        if args[0] == 'gb':
            channel = self.bot.get_channel(TEST2_CHANNEL_ID)
            message = ' '.join(args[1:])
        elif args[0] == 'test':
            channel = self.bot.get_channel(TEST_CHANNEL_ID)
            message = ' '.join(args[1:])
        else:
            channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
            message = ' '.join(args)
        logger.debug("{} {}".format(len(args), message))
        await channel.send(message)

    @commands.command(brief='Shows my host hardware-software info')
    async def sysinfo(self, ctx):
        await self._sysinfo(ctx)

    @cog_ext.cog_slash(name="sysinfo",
                       description='Shows my host hardware-software info',
                       #guild_ids=[207481917975560192, 572648167573684234],
                       )
    async def sysinfos(self, ctx: SlashContext):
        await self._sysinfo(ctx)

    async def _sysinfo(self, ctx):
        try:
            if ctx.author.id == int(ADMIN_ID):
                # wait_message = await ctx.send("Processing... Please wait. This might take sometime")
                # async with ctx.typing():
                embed = discord.Embed(
                    title="System Info",
                    description="Showing my host hardware/software information",
                    colour=discord.Color.gold()
                )
                embed.set_footer(text="Hope that was helpful, bye!")
                embed.set_author(name="Bro Bot", icon_url=self.bot.user.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)
                result = subprocess.Popen(['neofetch', '--stdout'], stdout=subprocess.PIPE)
                for line in result.stdout:
                    line = line.decode('utf-8').strip('\n').split(':')
                    if len(line) == 2:
                        if line[0] == "OS" or line[0] == "Host":
                            embed.add_field(name=line[0], value=line[1], inline=False)
                        else:
                            embed.add_field(name=line[0], value=line[1], inline=True)

                # Raspberry Pi Only!!!
                if os.uname()[1] == "raspberrypi":
                    temp = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
                    for line in temp.stdout:
                        line = line.decode('utf-8').strip('\n').split('=')
                        if len(line) == 2:
                            embed.add_field(name="CPU Temp", value=line[1], inline=True)

                    url = await get_public_url()
                    embed.add_field(name="Public URL", value=url, inline=False)

                    # await wait_message.edit(content='', embed=embed)
                    await embed_send(ctx, embed)
            else:
                await ctx.send('```Only my master can use this command.```')
        except Exception as e:
            logger.exception(e)

    @commands.command(brief='', hidden=True)
    async def runcmd(self, ctx, *args):
        logger.debug(args)
        if ctx.message.author.id == int(ADMIN_ID):
            try:
                result = subprocess.Popen(args, stdout=subprocess.PIPE)
                logger.debug(result.stdout)
                out = ""
                for line in result.stdout:
                    out += line.decode('utf-8')
                logger.debug(out)
                await ctx.send("```{}```".format(out))
            except Exception as e:
                logger.exception(e)
        else:
            await ctx.send('```Only my master can use this command.```')


def setup(bot):
    bot.add_cog(Admin(bot))
