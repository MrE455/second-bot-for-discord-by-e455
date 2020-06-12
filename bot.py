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
	emb.add_field(name = '{}exchange_rates'.format(PREFIX), value = 'Показать курс определённой валюты на сегодня. Список доступных валют: доллар, евро, биткоин, тенге, гривна, шекель. Пример: &exchange_rates шекель')
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

# Показывает курс валют.
@client.command()

async def exchange_rates (ctx, amount = None):
	await ctx.message.delete()

	if amount == 'доллар':
		URL = "https://www.google.com/search?q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+&aqs=chrome.1.69i57j0l7.9112j1j7&sourceid=chrome&ie=UTF-8"
		HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
		soup = BeautifulSoup(full_page.content, 'html.parser')
		full_page = requests.get(URL, headers = HEADERS)
		
		convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
		currency = convert[0].text
		
		await ctx.send("Один доллар равен " + currency + " рублей.")

	elif amount == 'евро':
		URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE&aqs=chrome..69i57j0l7.2879j1j7&sourceid=chrome&ie=UTF-8"
		HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
		full_page = requests.get(URL, headers = HEADERS)
		soup = BeautifulSoup(full_page.content, 'html.parser')
		
		convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
		currency = convert[0].text
		
		await ctx.send("Один евро равен " + currency + " рублей.")

	elif amount == 'биткоин':
		URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B1%D0%B8%D1%82%D0%BA%D0%BE%D0%B8%D0%BD%D0%B0&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B1%D0%B8%D1%82&aqs=chrome.0.0j69i57j0l6.3514j1j7&sourceid=chrome&ie=UTF-8"
		HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
		full_page = requests.get(URL, headers = HEADERS)
		soup = BeautifulSoup(full_page.content, 'html.parser')
		
		convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
		currency = convert[0].text
		
		await ctx.send("Один биткоин равен " + currency + " рублей.")

	elif amount == 'гривна':
		URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D1%8B&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B3%D1%80&aqs=chrome.1.69i57j0l7.6041j0j7&sourceid=chrome&ie=UTF-8"
		HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
		full_page = requests.get(URL, headers = HEADERS)
		soup = BeautifulSoup(full_page.content, 'html.parser')
		
		convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
		currency = convert[0].text
		
		await ctx.send("Одина гравна равна " + currency + " рублей.")

	elif amount == 'шекель':
		URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%B5%D0%BA%D0%B5%D0%BB%D1%8F&oq=%D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%B5&aqs=chrome.1.69i57j0l7.4277j1j7&sourceid=chrome&ie=UTF-8"
		HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
		full_page = requests.get(URL, headers = HEADERS)
		soup = BeautifulSoup(full_page.content, 'html.parser')
		
		convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
		currency = convert[0].text
		
		await ctx.send("Один шекель равен " + currency + " рублей.")

	elif amount == 'тенге':
		URL = "https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D1%82%D0%B5%D0%BD%D0%B3%D0%B5&oq=%D0%BA%D1%83%D1%80%D1%81+%D1%82%D0%B5&aqs=chrome.1.69i57j0l7.2317j1j7&sourceid=chrome&ie=UTF-8"
		HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
		
		full_page = requests.get(URL, headers = HEADERS)
		soup = BeautifulSoup(full_page.content, 'html.parser')
		
		convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
		currency = convert[0].text
		
		await ctx.send("Один тенеге равен " + currency + " рублей.")

	else:
		await ctx.send(f"**{ctx.author.mention}**, укажите валюту которую хотите просмотреть.")

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

# Запуск бота.
client.run(token)
