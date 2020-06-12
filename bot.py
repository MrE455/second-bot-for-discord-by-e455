import discord
from discord.ext import commands
import sqlite3
import os
from bs4 import BeautifulSoup
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
	emb.add_field(name = '{}dollar'.format(PREFIX), value = 'Показать курс доллара на сегодня. Пример: &dollar')
	#emb.add_field(name = '{}euro'.format(PREFIX), value = 'Показать курс евро на сегодня. Пример: &euro')
	#emb.add_field(name = '{}bitcoin'.format(PREFIX), value = 'Показать курс биткоина на сегодня. Пример: &bitcoin')
	#emb.add_field(name = '{}hryvnia'.format(PREFIX), value = 'Показать курс гривны на сегодня. Пример: &hryvnia')
	#emb.add_field(name = '{}shekel'.format(PREFIX), value = 'Показать курс шекеля на сегодня. Пример: &shekel')
	#emb.add_field(name = '{}tenge'.format(PREFIX), value = 'Показать курс тенге на сегодня. Пример: &tenge')
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

# Показывает курс доллара.
@client.command()

async def dollar (ctx):
	await ctx.message.delete()
	URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80%D0%B0&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE&aqs=chrome.0.69i59j69i57j0l5j69i60.4236j1j7&sourceid=chrome&ie=UTF-8"
	HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
	full_page = requests.get(URL, headers = HEADERS)
	soup = BeautifulSoup(full_page.content, 'html.parser')
		
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	dollar = convert[0].text
		
	await ctx.send("Один доллар равен " + dollar + " рублей.")

'''
# Показывает курс евро.
@client.command()

async def euro (ctx):
	URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE&oq=%D0%BA%D1%83%D1%80%D1%81+%D1%83&aqs=chrome.2.69i57j0l7.4295j0j7&sourceid=chrome&ie=UTF-8"
	HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
	
	full_page = requests.get(URL, headers = HEADERS)
	soup = BeautifulSoup(full_page.content, 'html.parser')
	
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	euro = convert[0].text
	
	await ctx.send("Один евро равен " + euro + " рублей.")

# Показывает курс биткоина.
@client.command()

async def bitcoin (ctx):
	URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B1%D0%B8%D1%82%D0%BA%D0%BE%D0%B8%D0%BD%D0%B0&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B1%D0%B8%D1%82&aqs=chrome.0.69i59j69i57j0l6.6197j0j7&sourceid=chrome&ie=UTF-8"
	HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
	
	full_page = requests.get(URL, headers = HEADERS)
	soup = BeautifulSoup(full_page.content, 'html.parser')
	
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	bitcoin = convert[0].text
	
	await ctx.send("Один биткоин равен " + bitcoin + " рублей.")

# Показывает курс гривны.
@client.command()

async def hryvnia (ctx):
	URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D1%8B&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B3%D1%80&aqs=chrome.0.69i59j69i57j0l6.14705j0j7&sourceid=chrome&ie=UTF-8"
	HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
	
	full_page = requests.get(URL, headers = HEADERS)
	soup = BeautifulSoup(full_page.content, 'html.parser')
	
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	hryvnia = hryvnia_convert[0].text
	
	await ctx.send("Одина гравна равна " + hryvnia + " рублей.")

# Показывает курс шекеля.
@client.command()

async def shekel (ctx):
	URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%B5%D0%BA%D0%B5%D0%BB%D1%8F&oq=%D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%B5&aqs=chrome.0.69i59j69i57j69i61l2.13899j1j7&sourceid=chrome&ie=UTF-8"
	HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
	
	full_page = requests.get(URL, headers = HEADERS)
	soup = BeautifulSoup(full_page.content, 'html.parser')
	
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	shekel = convert[0].text
	
	await ctx.send("Один шекель равен " + shekel + " рублей.")

# Показывает курс тенге.
@client.command()

async def tenge (ctx):
	URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D1%82%D0%B5%D0%BD%D0%B3%D0%B5&oq=%D0%BA%D1%83%D1%80%D1%81+%D1%82%D0%B5%D0%BD&aqs=chrome.0.69i59j69i57j0l6.3036j0j7&sourceid=chrome&ie=UTF-8"
	HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
	
	full_page = requests.get(URL, headers = HEADERS)
	soup = BeautifulSoup(full_page.content, 'html.parser')
	
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	tenge = convert[0].text
	
	await ctx.send("Один тенеге равен " + tenge + " рублей.")

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
'''

# Запуск бота.
client.run(token)
