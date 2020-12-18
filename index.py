import discord
from discord.ext import commands
import sqlite3
import random
import time

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute('''
		CREATE TABLE IF NOT EXISTS main(
			guild_id TEXT,
			user_id TEXT,
			wallet TEXT,
			bank TEXT
		)
	''')
	c.execute('''
		CREATE TABLE IF NOT EXISTS roles(
			guild_id TEXT,
			role_id TEXT
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS welcome(
			guild_id TEXT,
			channel_id TEXT,
			msg TEXT
		)
	''')
	print('Bot online')

@bot.event
async def on_member_join(member: discord.Member):
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT role_id FROM roles WHERE guild_id = {member.guild.id}')
	result = c.fetchone()
	if result is None:
		return;
	if result is not None:
		role = discord.utils.get(member.guild.roles, name=f'{result[0]}')
		await member.add_roles(role)
	c.execute(f'SELECT channel_id FROM welcome WHERE guild_id = {member.guild.id}')
	result1 = c.fetchone()
	if result1 is None:
		return;
	if result1 is not None:
		user = member.name
		mention = member.mention
		server = member.guild
		members = len(list(member.guild.members))
		c.execute(f'SELECT msg FROM welcome WHERE guild_id = {member.guild.id}')
		result2 = c.fetchone()
		channel = bot.get_channel(id=int(result1[0]))
		await channel.send(str(result2[0]).format(members=members, mention=mention, server=server, user=user))

@bot.command()
async def hi(ctx):
	mbed = discord.Embed(description=f"{ctx.message.author.mention} Hola como estas?", color=0x36393F)
	await ctx.send(embed=mbed)

@bot.command()
async def help(ctx):
	mbed = discord.Embed(title=":robot: __Comandos__", color=0x36393F)
	mbed.add_field(name=":hammer: Comandos de moderacion", value="`setautorole <@role>`\n`welcome`\n`purge`\n`kick`\n`ban`")
	mbed.add_field(name=":video_game: Comandos de entretenimiento", value="`gay <@user>`\n`punch <@user>`\n`roll`\n`hug`\n`kiss`\n`kill`\n`8ball`", inline=False)
	mbed.add_field(name=":moneybag: Economia", value="`work`\n`balance`\n**Solo moderadores**\n`add-money`\n`remove-money`")
	await ctx.send(embed=mbed)

@bot.command()
async def balance(ctx):
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT wallet, bank FROM main WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if result is None:
		mbed = discord.Embed(title=":moneybag: __Balance__", description=f"You don't have money :L", color=0x36393F)
	elif result is not None:
		mbed = discord.Embed(title=":moneybag: __Balance__", description=f"This user has {result[0]}$", color=0x36393F)
	await ctx.send(embed=mbed)

@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def work(ctx):
	ganancias = random.randrange(101)
	marcas = ['WallMart', 'Apple', 'KFC', 'Samsung', 'Tacobell', 'Discord']
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT wallet FROM main WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if result is None:
		sql = ("INSERT INTO main(wallet, user_id, guild_id) VALUES(?, ?, ?)")
		var = (ganancias, ctx.author.id, ctx.guild.id)
	if result is not None:
		sql = ("UPDATE main SET wallet = ? WHERE user_id = ? AND guild_id = ?")
		var = (int(result[0]) + ganancias, ctx.author.id, ctx.guild.id)
	c.execute(sql, var)
	db.commit()
	mbed = discord.Embed(title=f'__You work in {random.choice(marcas)}__', description=f"You Win {ganancias}$ Today :D", color=0x36393F)
	await ctx.send(embed=mbed)

@work.error
async def work_error(ctx, error):
	await ctx.send(error)

@bot.command()
async def say(ctx, *args):
	msg = " ".join(args)
	await ctx.send(msg)

@bot.command()
async def purge(ctx, amount=100):
	await ctx.channel.purge(limit=amount)

@bot.command(aliases=['remove-money'])
@commands.has_permissions(manage_guild=True)
async def remove_money(ctx, user: discord.Member, amount=None):
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT wallet FROM main WHERE user_id = {user.id} AND guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if amount is None:
		await ctx.send('No colocaste cuanto dinero quieres que le quite')
	elif amount is not None:
		sql = ("UPDATE main SET wallet = ? WHERE user_id = ? AND guild_id = ?")
		var = (int(result[0]) - int(amount), ctx.author.id, ctx.guild.id)
		c.execute(sql, var)
		db.commit()
		mbed = discord.Embed(title="__Removiendo dinero__", description=f"Removiste {amount}$ a {user}", color=0x36393F)
		await ctx.send(embed=mbed)

@remove_money.error
async def remove_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send('No tienes permiso para usar este comando')
	else:
		await ctx.send(error)

@bot.command(aliases=['add-money'])
@commands.has_permissions(manage_guild=True)
async def add_money(ctx, user: discord.Member, amount=None):
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT wallet FROM main WHERE user_id = {user.id} AND guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if amount is None:
		await ctx.send('No colocaste cuanto dinero quieres que le agregue')
	elif amount is not None:
		sql = ('UPDATE main SET wallet = ? WHERE user_id = ? AND guild_id = ?')
		var = (int(result[0]) + int(amount), user.id, ctx.guild.id)
		c.execute(sql, var)
		db.commit()
		mbed = discord.Embed(title="__Agregando dinero__", description=f"Le agregaste {amount}$ a {user}", color=0x36393F)
		await ctx.send(embed=mbed)

@add_money.error
async def money_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send('No tienes permisos suficientes para usar este comando')
	else:
		await ctx.send(error)

@bot.command()
async def gay(ctx, user: discord.Member):
	porcentaje = random.randrange(101)
	mbed = discord.Embed(title=":rainbow_flag: __Calculadora Gay__", description=f"{user} is a {porcentaje}% gay", color=0x36393F)
	mbed.set_image(url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Gay_Pride_Flag.svg/1200px-Gay_Pride_Flag.svg.png')
	await ctx.send(embed=mbed)

@gay.error
async def gay_error(ctx, error):
	mbed = discord.Embed(title=":x: No mencionaste a un usuario")

@bot.command()
async def roll(ctx):
	message = await ctx.send(f':stopwatch: Tirando dados...')
	time.sleep(4)
	await message.edit(content=f':game_die: Tiraste los dados y salio {random.randrange(1, 8)}')

@bot.command()
async def punch(ctx, user: discord.Member):
	if user.id == ctx.author.id:
		mbed = discord.Embed(description="No puedes golpearte a ti mismo", color=0x36393F)
	else:
		gifs = ['https://media.giphy.com/media/3xIxpCbXwoIlHGdfHA/giphy.gif', 'https://media2.giphy.com/media/3iyV9jWgQCLnSln00t/giphy.gif', 'https://media4.giphy.com/media/pVBXMhLmV1oJFzb8zl/giphy.gif']
		mbed = discord.Embed(description=f'{ctx.author} golpeo a {user}', color=0x36393F)
		mbed.set_image(url=random.choice(gifs))
	await ctx.send(embed=mbed)

@punch.error
async def p_error(ctx, error):
	mbed = discord.Embed(':x: No mencionaste a un usuario')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def setautorole(ctx, role: discord.Role):
	print(role.name)
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT role_id FROM roles WHERE guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if result is None:
		sql = ("INSERT INTO roles(role_id, guild_id) VALUES(?, ?)")
		val = (role.name, ctx.guild.id)
	elif result is not None:
		sql = ('UPDATE roles SET role_id = ? WHERE guild_id = ?')
		val = (role.name, ctx.guild.id)
	await ctx.send(f'Ahora, el rol {role.mention} se les asignara a todos los usuarios que ingresen al server')
	c.execute(sql, val)
	db.commit()

@bot.group(invoke_without_command=True)
async def welcome(ctx):
	mbed = discord.Embed(title="__Welcome configuration__", color=0x36393F)
	mbed.add_field(name=":mailbox_closed: Configurate a channel", value="`welcome channel <#channel>`")
	mbed.add_field(name=":page_facing_up: Configurate a message", value="`welcome message <message>`")
	await ctx.send(embed=mbed)

@welcome.command()
async def channel(ctx, channel: discord.TextChannel):
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT channel_id FROM welcome WHERE guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if result is None:
		sql = ('INSERT INTO welcome(guild_id, channel_id) VALUES(?, ?)')
		val = (ctx.guild.id, str(channel.id))
	elif result is not None:
		sql = ('UPDATE welcome SET channel_id = ? WHERE guild_id = ?')
		val = (str(channel.id), ctx.guild.id)

	await ctx.send(f'Welcome channel is now {channel}')
	c.execute(sql, val)		
	db.commit()

@channel.error
async def error(ctx, error):
	mbed = discord.Embed(':x: No seleccionaste un canal o el canal es invalido', color=0x36393F)
	await ctx.send(embed=mbed)

@welcome.command()
async def message(ctx, *, args):
	mbed = discord.Embed(title=f':white_check_mark: Welcome message has been set to \n`{args}`', color=0x36393F)
	db = sqlite3.connect('main.sqlite')
	c = db.cursor()
	c.execute(f'SELECT msg FROM welcome WHERE guild_id = {ctx.guild.id}')
	result = c.fetchone()
	if result is None:
		sql = ('INSERT INTO welcome(guild_id, msg) VALUES(?, ?)')
		val = (ctx.guild.id, args)
		await ctx.send(embed=mbed)
	elif result is not None:
		sql = ('UPDATE welcome SET msg = ? WHERE guild_id = ?')
		val = (args, ctx.guild.id)
		await ctx.send(embed=mbed)
	c.execute(sql, val)
	db.commit()

@bot.command()
async def kill(ctx, user: discord.Member):
	if user.id == ctx.author.id:
		await ctx.send('Oye, bro no lo hagas, no vale la pena :c')
	elif user.id == bot.user.id:
		await ctx.send('Que hice para merecer esto :,c')
	else:
		gifs = ['https://i.pinimg.com/originals/3c/ed/ee/3cedee4f8118855c83ea05463498f326.gif', 'https://www.icegif.com/wp-content/uploads/among-us-icegif-1.gif', 'https://media.tenor.com/images/d46c724d422714d738a84a51f1caf00b/tenor.gif', 'https://media1.tenor.com/images/361a7354f193af1b1ace5843dcaeeb02/tenor.gif?itemid=18599860']
		mbed = discord.Embed(description=f":knife: {ctx.author} asesino a {user}", color=0x36393F)
		mbed.set_image(url=random.choice(gifs))
		await ctx.send(embed=mbed)

@kill.error
async def error(ctx, error):
	await ctx.send('Debes mencionar a alguien')

@bot.command()
async def kiss(ctx, user: discord.Member):
	images = ['https://i.ytimg.com/vi/41NEnHO7rGo/maxresdefault.jpg', 'https://64.media.tumblr.com/28fd3feae07b8f32355bad331d0ef6c7/tumblr_mhet2eDOOV1rec05yo1_500.gif', 'https://64.media.tumblr.com/73cdbd6176cffb703e3c0ad02ec926ea/tumblr_mr6zbgfJHJ1so0fjho6_500.gifv', 'https://ist5-1.filesor.com/pimpandhost.com/8/7/0/4/87047/6/p/F/F/6pFFT/giphyg.gif']
	mbed = discord.Embed(description=f':heart: {ctx.author} beso a {user}', color=0x36393F)
	mbed.set_image(url=random.choice(images))
	await ctx.send(embed=mbed)

@kiss.error
async def error(ctx, error):
	await ctx.send('Menciona al usuario que quieras besas 7u7')

@bot.command()
async def hug(ctx, user: discord.Member):
	images = ['https://i.pinimg.com/originals/0a/16/52/0a1652de311806ce55820a7115993853.gif', 'https://media.tenor.com/images/cb9bffb9b0e88808fa156f2432233aa7/tenor.gif', 'https://media.tenor.com/images/f029c5ebf31f247eba1af1dc3a5f924e/tenor.gif', 'https://media.tenor.com/images/2bb9e56d8982c9e806d33aed404a62c0/tenor.gif']
	mbed = discord.Embed(description=f':heart: {ctx.author} abrazo a {user}', color=0x36393F)
	mbed.set_image(url=random.choice(images))
	await ctx.send(embed=mbed)

@hug.error
async def error(ctx, error):
	await ctx.send('Menciona al usuario que quieres abrazar :3')

@bot.command(aliases=['8ball'])
async def _8ball(ctx, *args):
	question = " ".join(args)
	respuestas = ['Posiblemente', 'Si', 'Por supuesto', 'Creo que si', 'No', 'Claro que no', 'Nunca']
	mbed = discord.Embed(title=':8ball: __Minijuego 8ball__', color=0x36393F)
	mbed.add_field(name=":question: Tu pregunta fue:", value=f'{question}', inline=False)
	mbed.add_field(name=":page_facing_up: Mi respuesta es:", value=f'{random.choice(respuestas)}')
	await ctx.send(embed=mbed)

@_8ball.error
async def error(ctx, error):
	await ctx.send('Tienes que preguntar algo')

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, args='No especifico una razon'):
	reason = " ".join(args)
	mbed = discord.Embed(title=":hammer: __Usuario kickeado correctamente__", color=0x36393F)
	mbed.add_field(name='Usuario: ', value=user)
	mbed.add_field(name='Razon: ', value=args, inline=False)
	mbed.add_field(name='Moderador responsable: ', value=ctx.author)
	try:
		await user.send(embed=mbed)
	except:
		await ctx.send('Algo salio mal al avisarle al usuario')
	try:
		await user.kick(reason=reason)
		await ctx.send(embed=mbed)
	except:
		await ctx.send('Algo salio mal en el proceso')

@kick.error
async def error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send('No tienes permisos para usar este comando')
	else:
		await ctx.send(error)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, args='No especifico una razon'):
	reason = "".join(args)
	mbed = discord.Embed(title=":hammer: __Usuario baneado correctamente__", color=0x36393F)
	mbed.add_field(name='Usuario: ', value=user)
	mbed.add_field(name='Razon: ', value=args, inline=False)
	mbed.add_field(name='Moderador responsable: ', value=ctx.author)
	try:
		await user.send(embed=mbed)
	except:
		await ctx.send('Algo salio mal al avisarle al usuario')
	try:
		await user.ban(reason=reason)
		await ctx.send(embed=mbed)
	except:
		await ctx.send('Algo salio mal en el proceso')

@ban.error
async def error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send('No tienes permisos para usar este comando')
	else:
		await ctx.send(error)

bot.run(TOKEN)