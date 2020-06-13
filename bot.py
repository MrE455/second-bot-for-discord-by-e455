import discord
from discord.ext import commands
import sqlite3
import os
from bs4 import BeautifulSoup as BS
import requests

PREFIX = '&'
token = os.environ.get('TOKEN')

# Устанавливаем префикс благодаря которым будут обозначаться команды.
# Удаляем встроенную команду "help" для дальнейшего создания своей команды.
client = commands.Bot(command_prefix = PREFIX)
client.remove_command('help')

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
@commands.has_permissions(administrator = True)

async def help (ctx):
	await ctx.message.delete()
	emb = discord.Embed(title = "Список команд данного бота:", colour = discord.Color.dark_orange())
	emb.add_field(name = '{}vk'.format(PREFIX), value = 'Ссылка на ВК автора.')
	emb.add_field(name = '{}telegram'.format(PREFIX), value = 'Ссылка на телеграм автора.')
	emb.add_field(name = '{}balance'.format(PREFIX), value = 'Узнать свой баланс (прсто ничего не указывайте) или баланс определённого пользователя. Пример: &balance @LOX')
	emb.add_field(name = '{}addition'.format(PREFIX), value = '(ВНИМАНИЕ только для MODERS и выше) Добавляет определёному пользователю введённое пользователем количество денег (не больше 1000000 за раз!). Пример: &addition @LOX 100')
	emb.add_field(name = '{}decrease'.format(PREFIX), value = '(ВНИМАНИЕ только для MODERS и выше) Убавляет определёному пользователю введённое пользователем количество денег (при вводе 666 отнимает все деньги!). Пример: &decrease @LOX 100')
	emb.add_field(name = '{}rate'.format(PREFIX), value = 'Показать курс валбты из списка: USD, EUR, BYN, KZT, PLN, UAH, GBR, CHF, JPY, CZK, TRY, CNY. Пример: &rate USD')
	emb.add_field(name = '{}add_role'.format(PREFIX), value = '(ВНИМАНИЕ только для MODERS и выше) Добавляет роль в магазин с введённой стоимостью от пользователя. Пример: &add_role_shop @TestRole 100000')
	emb.add_field(name = '{}remove_role'.format(PREFIX), value = '(ВНИМАНИЕ только для MODERS и выше) Убирает роль из магазина. Пример: &remove_role_shop @TestRole')
	emb.add_field(name = '{}shop_shop'.format(PREFIX), value = 'Показывает товары магазина.')
	emb.add_field(name = '{}buy_shop'.format(PREFIX), value = 'Покупает определённую роль которую выберит пользователь. Пример: &buy @TestRole')
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

async def addition (ctx, member: discord.Member = None, amount: int = 0):
	await ctx.message.delete()
	
	if member is None:
		await ctx.send(f"**{ctx.author.mention}**, укажите пользователя которому хотите добавить денег.")

	else:
		if amount > 1000000 or amount < 1:
			await ctx.send(f"**{ctx.author.mention}**, укажите количество денег.")
	
		else:
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
			connection.commit()
			await ctx.send("Зачисление {}$ на баланс пользователя {} успешно выполнено.".format(amount, member.mention))

# Команда позволяющая убавить определённое количество денег.
@client.command()
@commands.has_permissions(kick_members = True)

async def decrease (ctx, member: discord.Member = None, amount: int = 0):
	await ctx.message.delete()
	
	if member is None:
		await ctx.send(f"**{ctx.author.mention}**, укажите пользователя которому хотите убавить денег.")

	else:
		if amount < 1:
			await ctx.send(f"**{ctx.author.mention}**, укажите количестов денег.")

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

# Показывает курс валют.
@client.command()

async def rate (ctx, amount = None):
	await ctx.message.delete()
	URL = os.environ.get('url')
	HEADERS = {"User-Agent": os.environ.get('user-agent')}
	page = requests.get(URL, headers = HEADERS)
	soup = BS(page.content, 'html.parser')
	convert = soup.findAll("td")
	
	if amount == None:
		await ctx.send(f"**{ctx.author.mention}**, пожалуйста укажите валюту из списка.")
	
	elif amount == 'USD':
		await ctx.send("Один доллар равен " + convert[3].text + " рублей.")

	elif amount == 'EUR':
		await ctx.send("Один евро равен " + convert[8].text + " рублей.")

	elif amount == 'BYN':
		await ctx.send("Один белорусский рубль равен " + convert[29].text + " рублей.")

	elif amount == 'KZT':
		await ctx.send("Один казахский тенге равен " + convert[69].text + " рублей.")

	elif amount == 'PLN':
		await ctx.send("Один польский злотый равен " + convert[109].text + " рублей.")

	elif amount == 'UAH':
		await ctx.send("Одна украинская гривна равна " + convert[139].text + " рублям.")

	elif amount == 'GBR':
		await ctx.send("Один фунт стерлингов Соединённого королевства равен " + convert[144].text + " рублей.")

	elif amount == 'CHF':
		await ctx.send("Один швейцарский франк равен " + convert[159].text + " рублей.")

	elif amount == 'JPY':
		await ctx.send("Сто японских иен равны " + convert[169].text + " рублям.")

	elif amount == 'CZK':
		await ctx.send("Десять чешских крон равны " + convert[149].text + " рублям.")

	elif amount == 'TRY':
		await ctx.send("Одна турецкая лира равна " + convert[129].text + " рублям.")

	elif amount == 'CNY':
		await ctx.send("Десять китайских юаней равны " + convert[84].text + " рублям.")
	
	else:
		await ctx.send(f"**{ctx.author.mention}**, такой валюты нет в списке.")

# Добавить роль в магазин.
@client.command()
@commands.has_permissions(kick_members = True)

async def add_role (ctx, role: discord.Role = None, cost: int = 0):
	await ctx.message.delete()
	if role is None:
		await ctx.send(f"**{ctx.author.mention}**, укажите роль которую вы желаете добавить в магазин.")
	else:
		if cost < 1:
			await ctx.send(f"**{ctx.author.mention}**, укажите стоимость для данной роли.")
		else:
			cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
			connection.commit()
			await ctx.send(f"**{ctx.author.mention}**, роль была добавлена в магазин.")

# Убрать роль из магазина.
@client.command()
@commands.has_permissions(kick_members = True)

async def remove_role (ctx, role: discord.Role = None):
	await ctx.message.delete()
	if role is None:
		await ctx.send(f"**{ctx.author.mention}**, укажите роль которую хотите убрать из магазина.")
	else:
		cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
		connection.commit()
		await ctx.send(f"**{ctx.author.mention}**, роль была убрана из магазина.")

# Показать магазин.
@client.command()

async def shop_shop (ctx):
	await ctx.message.delete()
	embed = discord.Embed(title = 'Магазин')

	for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
		if ctx.guild.get_role(row[0]) != None:
			embed.add_field(name = f"Стоимость **{row[1]}$**", value = f"Вы приобритёте роль {ctx.guild.get_role(row[0]).mention}", inline = False)
		else:
			pass

	await ctx.send(embed = embed)

# Купить что-нибудь в магазине.
@client.command()

async def buy_shop (ctx, role: discord.Role = None):
	await ctx.message.delete()
	if role is None:
		await ctx.send(f"**{ctx.author.mention}**, укажите роль которую желаете приобристи.")
	
	else:
		if role in ctx.author.roles:
			await ctx.send(f"**{ctx.author.mention}**, такая роль у вас уже имеется.")
		
		elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
			await ctx.send(f"**{ctx.author.mention}**, у вас недостаточно средств.")
		
		else:
			await ctx.author.add_roles(role)
			cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
			connection.commit()
			await ctx.send(f"**{ctx.author.mention}**, вы приобрели роль.")

# Запуск бота.
client.run(token)
