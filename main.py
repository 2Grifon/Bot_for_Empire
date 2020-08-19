''' Основной файл в который будем импортировать sql'''

import discord, os
from discord.ext import commands
from discord.utils import get
import variables
from variables import *
from SQLite import WWDB

import sqlite3


class Base(commands.Cog):
    def __init__(self, bot):  # Иницилизация для работы регистра
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Hello, {ctx.message.author.mention}!')

    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=helpEmb)


class Game(commands.Cog, WWDB):
    def __init__(self, bot):  # Иницилизация для работы регистра
        self.conn = sqlite3.connect('sql.sqlite')
        self.curs = self.conn.cursor()
        self.bot = bot
        self.location = [i[1] for i in self.read_db('*', 'locations')]

    def check_category(ctx):  # функция для декоратора проверки категории
        return ctx.channel.category.id == 744483296032981093

    def check_reg_channel(ctx):
        return ctx.channel.id == 744484575341838367

    @commands.command()
    @commands.check(check_category)
    async def players_list(self, ctx):  # Пример просмотра листа зарегестрированных пользователей

        data = self.read_db('*', 'person')
        await ctx.send(
            'OK, {0}. Вот твои пользователи:\n {1}'.format(ctx.message.author.mention, data))

    @commands.command()
    @commands.check(check_reg_channel)
    async def register(self, ctx):  # Регистрация пользователей
        member = ctx.message.author
        role = get(member.guild.roles, name="test_role")  # получаем нужную роль

        if get(member.roles, name='test_role'):  # проверка существует ли у этого пользователя роль
            await ctx.send(f'{member.mention} - ты уже зарегистрирован!')

        else:
            self.enter_db('person(id,name,HP,LVL,curent_loc,inventory_weapons,inventory_armor,in_hand,on_body)',
                          (int(member.id), member.name, 10, 1, 'таверня', '1', '1', 1, 1))
            print(f'Роль {role} добавленна юзеру {member}!')
            await member.add_roles(role)
            await member.create_dm()
            await member.dm_channel.send(embed=regEmb)
            await ctx.send(f'{member.mention} - тебя зарегистрировали!')

    @commands.command()
    @commands.check(check_category)
    async def location(self, ctx, *args):

        if not args:
            await ctx.send(
                'Твоя локация - ' + self.read_db('curent_loc', f'person where id = {ctx.message.author.id}')[0][0])
        elif args[0] in self.location:
            self.update_db('person', 'curent_loc', f'{args[0]}', f'id={ctx.message.author.id}')
            await ctx.send(f'Локация изменина на {args[0]}')
        else:

            temp_for_writing = ''
            for i in range(len(self.location)):
                temp_for_writing += f'\n {i + 1}.' + self.location[i]
            await ctx.send('Нет такой локации, список доступных локаций:' + temp_for_writing)

    @commands.command()
    @commands.check(check_category)
    async def profile(self, ctx):
        try:
            data = self.read_db('*', f'person where id = {ctx.message.author.id}')[0]

            person_profile = discord.Embed(colour=discord.Colour.from_rgb(150, 206, 214))
            person_profile.set_author(name=f"{ctx.message.author.name}", icon_url=f'{ctx.message.author.avatar_url}')
            person_profile.add_field(
                name=f'Текущии характеристики:\nHP:  `{data[2]}` \nLVL:  `{data[3]}`\nТекущая локация: `{data[4]}`  ',
                # не забыть дописать!!!!
                value="Какую-нибудь писанину сюда добавте, ото оно без значения не работает",
                inline=False)

            await ctx.send(embed=person_profile)
        except Exception as err:
            print(err)


def main():
    TOKEN = os.environ.get('TOKEN_FOR_BOT')
    bot = commands.Bot(command_prefix='t! ')
    bot.remove_command(name='help')

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name}')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):  # отлов ошибки несуществубщей команды
            await ctx.send(embed=discord.Embed(
                description=f'**{ctx.author.name}**, данной команды не существует. Пожалуйста воспользуйтесь команндой **help** для полного списка команд.',
                color=discord.Colour.from_rgb(191, 56, 74)))
        if isinstance(error, commands.CheckFailure):  # отлов ошибки проверки
            await ctx.send(embed=discord.Embed(
                description=f'**{ctx.author.name}**, вы используете команду не в том канале. Пожалуйста воспользуйтесь команндой **help** для определения необходимой категории.',
                color=discord.Colour.from_rgb(191, 56, 74)))

    bot.add_cog(Base(bot))
    bot.add_cog(Game(bot))

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
