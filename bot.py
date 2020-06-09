from config import settings
import discord
from discord.ext import commands
import sqlite3

# Устанавливаем префикс благодаря которым будут обозначаться команды.
# Удаляем встроенную команду "help" для дальнейшего создания своей команды.

client = commands.Bot(command_prefix = settings['PREFIX'])
client.remove_command('help')

# Даёт возможность работать с ошибками.
@client.event

async def on_command_error (ctx, error):
	pass

# Подключение базы данных и создание переменной для управления базы данных.
connection = sqlite3.connect('server.db')
cursor = connection.cursor()

# Функция создания таблицы и добавления нового пользователя если его ещё нет.
@client.event

async def on_ready ():
	print('[LOG]BOT was connected.')
	await client.change_presence(status = discord.Status.online, activity = discord.Game('правительство РФ'))
	cursor.execute("""CREATE TABLE IF NOT EXISTS users (name TEXT, id INT, cash BIGINT, rep INT, lvl INT)""")

	for guild in client.guilds:
		for member in guild.members:
			if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")

			else:
				pass

	connection.commit()

@client.event

async def on_member_join (member):
	if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")
		connection.commit()

	else:
		pass

# Команда help.

@client.command()

async def help (ctx):
	await ctx.message.delete()
	emb = discord.Embed(title = "Список команд данного бота:", colour = discord.Color.dark_orange())
	emb.add_field(name = '{}vk'.format(settings['PREFIX']), value = 'Ссылка на ВК автора.')
	emb.add_field(name = '{}telegram'.format(settings['PREFIX']), value = 'Ссылка на телеграм автора.')
	emb.add_field(name = '{}balance'.format(settings['PREFIX']), value = 'Узнать свой баланс (прсто ничего не указывайте) или баланс определённого пользователя. Пример: &balance @LOX')
	emb.add_field(name = '{}addition'.format(settings['PREFIX']), value = 'Добавляет определёному пользователю введённое пользователем количество денег (не больше 1000000 за раз!). Пример: &addition @LOX 100')
	emb.add_field(name = '{}balance'.format(settings['PREFIX']), value = 'Убавляет определёному пользователю введённое пользователем количество денег (при вводе 666 отнимает все деньги!). Пример: &decrease @LOX 100')
	await ctx.send(embed = emb)

# Команда показывает количество денег определённого пользователя.
@client.command()

async def balance (ctx, member: discord.Member = None):
	await ctx.message.delete()
	
	if member is None:
		await ctx.send(embed = discord.Embed(description = f"""Ваш баланс составляет: **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}**$"""))
	
	else:
		await ctx.send(embed = discord.Embed(description = f"""Баланс пользователя: **{member.mention}**\nСоставляет: **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}**$"""))

# Команда позволающая добавить определённое количество денег.
@client.command()
@commands.has_permissions(kick_members = True)

async def addition (ctx, member: discord.Member = None, amount: int = None):
	await ctx.message.delete()
	
	if member is None or amount > 1000000 or amount < 1:
		await ctx.send(f"**{ctx.author.mention}**, укажите пользователя, которому хотите добавить денег, и количество денег.")
	
	else:
		cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
		connection.commit()
		await ctx.send("Зачисление {}$ на баланс пользователя {} успешно выполнено.".format(amount, member.mention))

# Команда позволяющая убавить определённое количество денег.
@client.command()
@commands.has_permissions(kick_members = True)

async def decrease (ctx, member: discord.Member = None, amount: int = None):
	await ctx.message.delete()
	
	if member is None or amount < 1:
		await ctx.send(f"**{ctx.author.mention}**, укажите пользователя, которому хотите убавить денег.")

	elif amount == 666:
		cursor.execute("UPDATE users SET cash = {} WHERE id = {}".format(0, member.id))
		connection.commit()
		await ctx.send("Вывод всех денег с баланса пользователя {} успешно выполнен.".format(member.mention))
	
	else:
		cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, member.id))
		connection.commit()
		await ctx.send("Вывод {}$ с баланса пользователя {} успешно выполнен.".format(amount, member.mention))

# Ссылка на Вк.
@client.command()

async def vk (ctx):
	await ctx.message.delete()
	emb = discord.Embed(title = 'Vk:', colour = discord.Color.red())
	emb.set_footer(text = client.user.name, icon_url = client.user.avatar_url)
	emb.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/VK.com-logo.svg/250px-VK.com-logo.svg.png')
	emb.add_field(name = "Ссылка:", value = "https://vk.com/mr_e455")
	await ctx.send(embed = emb)

# Ссылка на телеграм.
@client.command()

async def telegram (ctx):
	await ctx.message.delete()
	emb = discord.Embed(title = 'Telegram', colour = discord.Color.dark_red())
	emb.set_footer(text = client.user.name, icon_url = client.user.avatar_url)
	emb.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/5/5c/Telegram_Messenger.png')
	emb.add_field(name = "Имя:", value = "@mr_e455")
	await ctx.send(embed = emb)

# Работа с ошибками.
@addition.error

async def addition_error (ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.message.delete()
		await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав для использования данной команды.')

@decrease.error

async def decrease_error (ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.message.delete()
		await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав для использования данной команды.')

# Запуск бота.
client.run(settings['TOKEN'])