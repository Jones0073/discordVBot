import os
import json
import pickle
import datetime
import discord
from io import BytesIO
from os.path import exists
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands,  tasks
from discord.ui import View, Button, Modal
from PIL import Image, ImageFont, ImageDraw
import platform 


variables = {
    "ausweis_vorlage_Windows" : "C:/Users/Jonathan/Pictures/ausweis_vorlage.png",
    "ausweis_vorlage_Linux"   : "/home/pi/Python/ausweis_vorlage.png",

    "pfad_Windows": "",
    "pfad_Linux:": "/home/pi/Python/",

    "bot_key_Windows": "OTkzODY4NTc0ODgyMDI1NTMz.GaoFz3.YGITPFzMGG9sQmM_8uam9jydKfFjJEKW3bkAo8",
    "bot_key_Linux": "MTAxNDg3OTUyODAxNjkzNzAxMA.GxRzcZ.kLajnHsIIyF3BoNHO6dXQybSB3d-sv72E-7aCs",
}


def variable(input) -> str:
    s = platform.system()
    return variables[input + "_" + s]


class Data():

    def __init__(self, filename = "rpg_data.dat"):
        self.filename = filename
        if exists(self.filename):
            self.load()
        else:
            self.data = {
                "locked": [],
                "character": {},
                "items": {
                    "Auto": 10,
                    "Ausweis": "Noch nicht verfügbar!",
                    "Schere": "Schnipp, Schnapp, ab!",
                    "Axt": "Der Erzfeind der Bäume!",
                    "Spitzhacke": "Plötzlich Minecraft.",
                    "Stein": "Hart!",
                    "Brett": "Daraus kann man was Bauen!",
                    "Wein": "So rot wie Blut",
                    "Limonade": "Uhh... Sauer!",
                    "Tabak": "Kann man verbrennen.",
                    "Kokain": "Achtung: Illegal!",
                    "Weed": "Achtung: Illegal!",
                },
                "item_log": {
                    1: "Ausweis",
                    -1: {"name": "Auto", "id": 1, "inv": []},
                },
                "loops": {
                    "team_liste": {
                        "channel": None,
                        "msg_id": None
                    },
                    "farming": {},
                },
            }
            self.save()
            self.show()
            self.logger = None


    def log(self, *msg):
        msg = " ".join(msg)
        print(msg)


    def show(self):
        print(json.dumps(self.data, sort_keys = False, indent = 2),"\n")


    def get(self, id, key):
        if not self.exists(id):
            return
        
        if not key in self.data[id]:
            return

        return self.data[id][key]


    def save(self):
        with open(self.filename, "wb") as file:
            pickle.dump(self.data, file)
        self.log(self.filename, "saved")


    def load(self):
        with open(self.filename, "rb") as file:
            self.data = pickle.load(file)
        self.log(self.filename, "loaded")


    def create_character(self, id, vor_name, nach_name):
        self.data["character"][id] = {
                "vor_name": vor_name,
                "nach_name": nach_name,
                "purse": 0,
                "bank": 0,
                "inv": [],
            }
        self.save()


    def remove_money(self, id, amount, target):
        self.data["character"][id][target] -= amount
        self.save()


    def give_money(self, id, amount, target):
        self.data["character"][id][target] += amount
        self.save()


    def exists(self, id):
        if id not in self.data:
            return False
        return True


    def create_item(self, name: str, msg: str):
        self.data["items"][name] = msg
        self.save()


    def create_storage(self, name: str, space: int):
        self.data["items"][name] = space
        self.save()


    def give_item(self, id: int, item_name: str):
        item_id = self.log_item(item_name)

        self.data["character"][id]["inv"].append(item_id)
        self.save()


    def give_storage(self, id: int, storage_name: str):
        storage_id = self.log_storage(storage_name)

        self.data["character"][id]["inv"].append(storage_id)
        self.save()


    def log_item(self, item_name: str):
        last = self.data["item_log"].keys()
        l = sorted(last, reverse = True)
        new_id = l[0] + 1
        self.data["item_log"][new_id] = item_name
        self.save()
        return new_id


    def log_storage(self, storage_name: str):
        last = self.data["item_log"].keys()
        l = sorted(last)
        new_id = l[0] - 1
        id = self.data["item_log"][l[0]]["id"] + 1
        self.data["item_log"][new_id] = {"name": storage_name, "id": id, "inv": []}
        self.save()
        return new_id


class WhitelistModal(Modal, title = "Whitelist Fragebogen"):
    name = discord.ui.TextInput(label = "[OOC] Wie heißt du?")
    alter = discord.ui.TextInput(label = "[OOC] Wie alt bist du?")
    club_name = discord.ui.TextInput(label = "[OOC] Wie lautet dein Social Club Name?")
    wie_zu_uns = discord.ui.TextInput(label = "[OOC] Wie bist du auf uns gekommen?")
    erfahrung = discord.ui.TextInput(label = "[OOC] Hast du RP Erfahrung?")

    async def on_submit(self, interaction: discord.Interaction):
        c = client.get_channel(1074685216435744830)
        embed1 = discord.Embed(title = f"{interaction.user.name} hat sich beworben!",color = 0xf2aa0d)
        embed1.add_field(name = "1. [OOC] Wie heißt du?", value = self.name, inline = False)
        embed1.add_field(name = "2. [OOC] Wie alt bist du?", value = self.alter, inline = False)
        embed1.add_field(name = "3. [OOC] Wie lautet dein Social Club Name?", value = self.club_name, inline = False)
        embed1.add_field(name = "4. [OOC] Wie bist du auf uns gekommen?", value = self.wie_zu_uns, inline = False)
        embed1.add_field(name = "5. [OOC] Hast du RP Erfahrung?", value = self.erfahrung, inline = False)
        await c.send(embed = embed1)
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Deine Antworten wurden dem Support erfolgreich übermittelt! Bitte fülle nun die anderen Fragebögen aus oder warte bis sich ein Supporter bei dir meldet.", inline = True)
        await interaction.response.send_message(embed = embed)


class WhitelistModalIC(Modal, title = "Whitelist Fragebogen"):
    ic_name = discord.ui.TextInput(label = "Wie heißt dein Charakter?")
    ic_geburtstag = discord.ui.TextInput(label = "Wann ist der Geburtstag deines Charakters?")
    ic_alter = discord.ui.TextInput(label = "Wie alt ist dein Charakter?")
    ic_woher = discord.ui.TextInput(label = "Woher kommt dein Charakter?")
    ic_vorgeschichte = discord.ui.TextInput(label = "Vorgeschichte von deinem Charakter:", min_length = 100, style = discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        c = client.get_channel(1074685216435744830)
        embed1 = discord.Embed(title = f"{interaction.user.name} hat sich beworben!",color = 0xf2aa0d)
        embed1.add_field(name = "6. [IC] Wie heißt dein Charakter?", value = self.ic_name, inline = False)
        embed1.add_field(name = "7. [IC] Wann ist der Geburtstag deines Charakters?", value = self.ic_geburtstag, inline = False)
        embed1.add_field(name = "8. [IC] Wie alt ist dein Charakter?", value = self.ic_alter, inline = False)
        embed1.add_field(name = "9. [IC] Woher kommt dein Charakter?", value = self.ic_woher, inline = False)
        embed1.add_field(name = "10. [IC] Vorgeschichte:", value = self.ic_vorgeschichte, inline = False)
        await c.send(embed = embed1)
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Deine Antworten wurden dem Support erfolgreich übermittelt! Bitte fülle nun die anderen Fragebögen aus oder warte bis sich ein Supporter bei dir meldet.", inline = True)
        await interaction.response.send_message(embed = embed)


class WhitelistModalRules(Modal, title = "Whitelist Fragebogen"):
    hoechstes_gut = discord.ui.TextInput(label = "Was ist dein höchstes Gut?")
    ic_ooc = discord.ui.TextInput(label = "Was ist IC und was ist OOC?")
    rdm_vdm = discord.ui.TextInput(label = "Was ist RDM und VDM?")
    savezonen = discord.ui.TextInput(label = "Welche Savezones gibt es?")
    schussankuendigung = discord.ui.TextInput(label = "Wird eine Schussankündigung benötigt?")

    async def on_submit(self, interaction: discord.Interaction):
        c = client.get_channel(1074685216435744830)
        embed1 = discord.Embed(title = f"{interaction.user.name} hat sich beworben!",color = 0xf2aa0d)
        embed1.add_field(name = "11. [Regeln] Was ist dein höchstes Gut?", value = self.hoechstes_gut, inline = False)
        embed1.add_field(name = "12. [Regeln] Was ist IC und was ist OOC?", value = self.ic_ooc, inline = False)
        embed1.add_field(name = "13. [Regeln] Was ist RDM und VDM?", value = self.rdm_vdm, inline = False)
        embed1.add_field(name = "14. [Regeln] Welche Savezones gibt es?", value = self.savezonen, inline = False)
        embed1.add_field(name = "15. [Regeln] Wir eine Schussankündigung benötigt?", value = self.schussankuendigung, inline = False)
        await c.send(embed = embed1)
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Deine Antworten wurden dem Support erfolgreich übermittelt! Bitte fülle nun die anderen Fragebögen aus oder warte bis sich ein Supporter bei dir meldet.", inline = True)
        await interaction.response.send_message(embed = embed)


data = Data()
data.show()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(
    command_prefix = "!", 
    help_command = None,
    intents = intents
)

@client.event
async def setup_hook():
    data.data["loops"]["team_liste"]["channel"] = None
    data.data["loops"]["team_liste"]["msg_id"] = None
    data.save()
    loop.start()


@client.event
async def on_ready():
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "ULTIMATE V"))


@client.command()
@commands.has_role("⚙️-Bot Developer")
async def sync(ctx):
    await client.tree.sync()
    print("Synced the Bot.")


@sync.error
async def sync_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        print(f"{ctx.author} tried to use /sync command.")
    else:
        print(error)



# AUTOCOMPLETION #



async def item_autocompletion(interaction: discord.Interaction, current: str):
    words = []
    for item in data.data["items"].keys():
        # Kann nicht mehr als 25 verarbeiten
        if len(words) == 25:
            break
        if current.lower() in item.lower():
            words.append(app_commands.Choice(name = item, value = item))
    return words




@client.tree.command(name = "bewerben", description = "Fülle einen Fragebogen aus um dich für die Whitelist zu bewerben!")
@app_commands.choices(fragebogen = [
    Choice(name = "OOC", value = 1),
    Choice(name = "IC", value = 2),
    Choice(name = "Regeln", value = 3)
])
async def bewerben(interaction: discord.Integration, fragebogen: Choice[int]):
    if fragebogen.value == 1:
        await interaction.response.send_modal(WhitelistModal())
    if fragebogen.value == 2:
        await interaction.response.send_modal(WhitelistModalIC())
    if fragebogen.value == 3:
        await interaction.response.send_modal(WhitelistModalRules())



# CHARAKTERE #



@client.tree.command(name = "charakter_erstellen", description = "Erstelle einene Charakter für eine Person.")
async def charakter_erstellen(interaction: discord.Interaction, besitzer: discord.Member, vor_name: str, nach_name: str):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer.id in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat bereits einen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    data.create_character(besitzer.id, vor_name, nach_name)
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = "Der Charakter wurde erfolgreich erstellt!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "charakter_löschen", description = "Lösche einene Charakter von einer Person.")
async def charakter_loeschen(interaction: discord.Interaction, besitzer: discord.Member):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    del data.data["character"][besitzer.id]
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = "Der Charakter wurde erfolgreich gelöscht!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "charakter_liste", description = "Zeigt dir alle Charaktere und dessen Besitzer die es derzeit gibt.")
async def charakter_liste(interaction: discord.Interaction):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(data.data["character"].keys()) == 0:
        embed = discord.Embed(color = 0xf2aa0d)
        embed.add_field(name = "Charaktere:", value = "Es gibt keine Charaktere.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    msg = ""
    for c in data.data["character"].keys():
        name = data.data["character"][c]["vor_name"] + " " + data.data["character"][c]["nach_name"]
        msg += f"{name}: <@{str(c)}>\n"

    embed = discord.Embed(color = 0xf2aa0d)
    embed.add_field(name = "Charaktere:", value = msg, inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "ausweis_generieren", description = "Erstelle einen Personalausweis.")
async def generate_id_card(interaction: discord.Interaction, vor_name: str, nach_name: str, geburts_datum: str, geburts_ort: str, besitzer: discord.Member):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    buffer = BytesIO()

    with Image.open(variable("ausweis_vorlage")) as im:
        text_font = ImageFont.truetype("Roboto-Regular.ttf", 100)
        n_font = ImageFont.truetype("Roboto-Medium.ttf", 50)
        draw = ImageDraw.Draw(im)

        draw.text((390, 520), vor_name, (0, 0, 0), font = text_font)
        draw.text((1100, 520), nach_name, (0, 0, 0), font = text_font)
        draw.text((390, 700), geburts_datum, (0, 0, 0), font = text_font)
        draw.text((390, 880), geburts_ort, (0, 0, 0), font = text_font)
        draw.text((1600, 1070), str(besitzer.id), (0, 0, 0), font = n_font)
        im.save(buffer, "png")
        buffer.seek(0)


    save_button = Button(label = "Speichern", style = discord.ButtonStyle.success, emoji = "✔️")
    delete_button = Button(label = "Löschen", style = discord.ButtonStyle.danger, emoji = "❌")

    async def save_button_callback(interaction):
        picture = Image.open(buffer)
        picture.save(f"/home/pi/ausweise/{str(besitzer.id)}.png")
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = "Der Ausweis wurde erfolgreich erstellt!", inline = True)
        await interaction.response.send_message(embed = embed)
    save_button.callback = save_button_callback

    async def delete_button_callback(interaction):
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = "Der Ausweis wurde erfolgreich gelöscht!", inline = True)
        await interaction.response.send_message(embed = embed)
    delete_button.callback = delete_button_callback


    view = View()
    view.add_item(save_button)
    view.add_item(delete_button)


    file = discord.File(fp = buffer, filename = "ausweis.png")
    await interaction.response.send_message(file = file, view = view)


@client.tree.command(name = "ausweis_zeigen", description = "Zeige deinen Personalausweis.")
async def show_id_card(interaction: discord.Interaction, besitzer: discord.Member):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer is None:
        if exists(f"/home/pi/ausweise/{str(interaction.user.id)}.png"):
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Du hast noch keinen Personalausweis!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        else:
            await interaction.response.send_message("Du hast keinen Personalausweis.")
            return

    # !! ES FEHLT EINE BERECHTIGUNGS ABRFRAGE !! #

    if exists(f"/home/pi/ausweise/{str(besitzer.id)}.png"):
        await interaction.response.send_message(file = discord.File(f"/home/pi/ausweise/{str(besitzer.id)}.png"))
        return
    else:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Personalausweis!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)


@client.tree.command(name = "ausweis_entfernen", description = "Entfernt den Personalausweis einer Person.")
async def show_id_card(interaction: discord.Interaction, besitzer: discord.Member):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if not exists(f"/home/pi/ausweise/{str(besitzer.id)}.png"):
        await interaction.response.send_message("Dieser User hat keinen Personalausweis.")
        return
    
    os.remove(f"/home/pi/ausweise/{str(besitzer.id)}.png")
    await interaction.response.send_message("Der Personalausweis wurde erfolgreich gelöscht!")


@client.command()
async def ausweis_bild(ctx, besitzer: discord.Member):

    if ctx.author.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await ctx.send(embed = embed, ephemeral = True)
        return

    if not exists(f"/home/pi/ausweise/{str(besitzer.id)}.png"):
        await ctx.send("Dieser User hat keinen Personalausweis.")
        return

    if len(ctx.message.attachments) != 1:
        await ctx.send("Bitte hänge **eine** Nachricht and den Command.")
        return

    filename, file_extension = os.path.splitext(ctx.message.attachments[0].filename)
    if file_extension.upper() not in [".PNG", ".JPG", ".JPEG", ] :
        await ctx.send("Bitte lade das Bild als ***.png*** Datei hoch.")
        return

    p_data = BytesIO(await ctx.message.attachments[0].read())

    pfp = Image.open(p_data)
    pfp = pfp.resize((530, 530))
    ausweis = Image.open(f"/home/pi/ausweise/{str(besitzer.id)}.png")

    ausweis.paste(pfp, (1630, 0))
    ausweis.save(f"/home/pi/ausweise/{str(besitzer.id)}.png")
    await ctx.send("Das Foto wurde erfolgreich hinzugefügt. Sieh es dir mit /ausweis_zeigen an.")



# ECONOMY SYSTEM #



@client.tree.command(name = "konto", description = "Zeigt wie viel Geld du gerade in deiner Brieftasche & Bank hast.")
async def bal(interaction: discord.Interaction, besitzer: discord.Member = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer:
        if besitzer.id not in data.data["character"].keys():
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        purse = data.data["character"][besitzer.id]["purse"]
        bank = data.data["character"][besitzer.id]["bank"]
        name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]

        embed = discord.Embed(title = f"{name}s Brieftasche:", color = 0xf2aa0d)
        embed.add_field(name = "Bank", value = str(bank) + "$", inline = True)
        embed.add_field(name = "Brieftasche", value = str(purse) + "$", inline = True)
        embed.add_field(name = "Total", value = str(bank + purse) + "$", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    purse = data.data["character"][interaction.user.id]["purse"]
    bank = data.data["character"][interaction.user.id]["bank"]
    name = data.data["character"][interaction.user.id]["vor_name"] + " " + data.data["character"][interaction.user.id]["nach_name"]

    embed = discord.Embed(title = f"{name}s Brieftasche:", color = 0xf2aa0d)
    embed.add_field(name = "Bank", value = str(bank) + "$", inline = True)
    embed.add_field(name = "Brieftasche", value = str(purse) + "$", inline = True)
    embed.add_field(name = "Total", value = str(bank + purse) + "$", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "konto_best", description = "Zeigt dir die top 10 Spieler mit dem Meisten Geld insgesamt.")
async def baltop(interaction: discord.Interaction):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(data.data["character"].keys()) <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Es sind zu wenig Charaktere vorhanden!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return
    
    character = data.data["character"]
    result = sorted(character.items(), key = lambda x: x[1]["purse"] + x[1]["bank"], reverse = True)

    anzahl = len(data.data["character"].keys())
    if anzahl > 10:
        anzahl = 10
    count = 0
    top = ""

    for i in range(anzahl):

        first = result[count][1]["vor_name"]
        last = result[count][1]["nach_name"]
        money = result[count][1]["bank"] + result[count][1]["purse"]

        msg = f"{count + 1}. {first} {last}: {money:,}$\n"  #.replace(',','.')
        top += msg
        count += 1
    
    embed = discord.Embed(color = 0xf2aa0d)
    embed.add_field(name = "Die reichsten Spieler:", value = top, inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "einzahlen", description = "Überweise Geld aus deiner Brieftasche in deine Bank.")
async def deposit(interaction: discord.Interaction, menge: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if data.data["character"][interaction.user.id]["purse"] <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast kein Geld in deiner Brieftasche!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge:
        if menge <= 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Bitte gib eine Zahl über 0 an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if data.data["character"][interaction.user.id]["purse"] < menge:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Du hast nicht so viel Geld in deiner Brieftasche!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        data.remove_money(interaction.user.id, menge, "purse")
        data.give_money(interaction.user.id, menge, "bank")
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"{menge}$ wurden erfolgreich in deine Bank überwiesen!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    purse = data.data["character"][interaction.user.id]["purse"]

    data.remove_money(interaction.user.id, purse, "purse")
    data.give_money(interaction.user.id, purse, "bank")
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"{purse}$ wurde erfolgreich in deine Bank überwiesen!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "auszahlen", description = "Überträgt Geld von deinem Bankkonto in deine Brieftasche.")
async def withdraw(interaction: discord.Interaction, menge: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if data.data["character"][interaction.user.id]["bank"] <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast kein Geld auf deinem Bankkonto!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge:
        if menge <= 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Bitte gib eine Zahl über 0 an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if data.data["character"][interaction.user.id]["bank"] < menge:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Du hast nicht so viel Geld auf deinem Bankkonto!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        data.remove_money(interaction.user.id, menge, "bank")
        data.give_money(interaction.user.id, menge, "purse")
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"{menge}$ wurden erfolgreich in deine Brieftasche gelegt!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    bank = data.data["character"][interaction.user.id]["bank"]

    data.remove_money(interaction.user.id, bank, "bank")
    data.give_money(interaction.user.id, bank, "purse")
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"{bank}$ wurden erfolgreich in deine Brieftasche gelegt!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "bezahlen", description = "Nimmt Geld aus deiner Brieftasche und legt dieses in die Brieftasche der anderen Person.")
async def bezahlen(interaction: discord.Interaction, person: discord.Member, menge: int):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id == person.id:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst kein Geld an dich selber überweisen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if person.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib eine Zahl über 0 an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if data.data["character"][interaction.user.id]["purse"] < menge:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Geld in deiner Brieftasche!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    data.remove_money(interaction.user.id, menge, "purse")
    data.give_money(person.id, menge, "purse")
    name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"{menge}$ wurden erfolgreich an {name} überwiesen!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "geld_geben", description = "Dieser befehl erstellt neues Geld und legt es entweder in die Bank oder Brieftasche der Person.")
@app_commands.choices(ziel = [
    Choice(name = "Bank", value = 1),
    Choice(name = "Brieftasche", value = 2)
])
async def give_money_(interaction: discord.Interaction, person: discord.Member, ziel: Choice[int], menge: int):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if person.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib eine Zahl über 0 an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if ziel.name == "Bank":
        data.give_money(person.id, menge, "bank")
        name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"{menge}$ wurden erfolgreich an {name} überwiesen!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if ziel.name == "Brieftasche":
        data.give_money(person.id, menge, "purse")
        name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"{menge}$ wurden erfolgreich an {name} überwiesen!", inline = True)
        await interaction.response.send_message(embed = embed)
        return


@client.tree.command(name = "setz_geld", description = "Setzt den Kontostand und/oder die Brieftasche auf ein bestimmeten betrag.")
async def set_money(interaction: discord.Interaction, person: discord.Member, bank: int = None, brieftasche: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if person.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if bank is None and brieftasche is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib an, von was du das Geld bestimmen willst!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if bank is None:
        bank = data.data["character"][person.id]["bank"]

    if brieftasche is None:
        brieftasche = data.data["character"][person.id]["purse"]

    data.data["character"][person.id]["bank"] = bank
    data.data["character"][person.id]["purse"] = brieftasche
    data.save()

    name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Das Geld von {name} wurde erfolgreich gesetzt!", inline = True)
    await interaction.response.send_message(embed = embed)



# MODERATION COMMANDS #



@client.tree.command(name = "vipe", description = "Setzt Spielerdaten auf 0. Darin ist zum Beispiel der Kontostand, Brieftasche und Inventar.")
@app_commands.choices(ziel = [
    Choice(name = "Alles", value = 1),
    Choice(name = "Bank", value = 2),
    Choice(name = "Brieftasche", value = 3),
    Choice(name = "Inventar", value = 4)
])
async def vipe(interaction: discord.Interaction, person: discord.Member, ziel: Choice[int]):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if person.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return
    
    if ziel.name == "Alles":
        data.data["character"][person.id]["bank"] = 0
        data.data["character"][person.id]["purse"] = 0
        data.data["character"][person.id]["inv"] = [None] * 10
        data.save()

        name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Der Charakter {name} wurde erfolgreich geviped!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if ziel.name == "Bank":
        data.data["character"][person.id]["bank"] = 0
        data.save()

        name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Die Bank von {name} wurde erfolgreich geviped!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if ziel.name == "Brieftasche":
        data.data["character"][person.id]["purse"] = 0
        data.save()

        name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Die Purse von {name} wurde erfolgreich geviped!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if ziel.name == "Inventar":
        data.data["character"][person.id]["inv"] = []
        data.save()

        name = data.data["character"][person.id]["vor_name"] + " " + data.data["character"][person.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Das Inventar von {name} wurde erfolgreich geviped!", inline = True)
        await interaction.response.send_message(embed = embed)
        return


@client.tree.command(name = "lock", description = "Sperrt einen Spieler von allen Befehlen.")
async def lock(interaction: discord.Interaction, person: discord.Member):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if person.id in [733797516096831508, 697050286677557259, 470293837936590849]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"Du kannst <@{person.id}> nicht sperren!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if person.id in data.data["locked"]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person ist bereits gesperrt!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    data.data["locked"].append(person.id)
    data.save()

    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"<@{person.id}> wurde erfolgreich gesperrt und kann nun keine Befehle mehr verschicken!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "unlock", description = "Entperrt einen Spieler vom /lock Befehl. Dieser kann nun wieder normal alle befehle benutzen.")
async def unlock(interaction: discord.Interaction, person: discord.Member):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if person.id not in data.data["locked"]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person ist nicht gesperrt!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    data.data["locked"].remove(person.id)
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"<@{person.id}> wurde erfolgreich entsperrt und kann nun wieder Befehle verschicken!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "lock_liste", description = "Zeigt dir alle derzeit gesperrten Spieler.")
async def lock_liste(interaction: discord.Interaction):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(data.data["locked"]) == 0:
        embed = discord.Embed(color = 0xf2aa0d)
        embed.add_field(name = "Gesperrte Spieler:", value = "Es sind zur Zeit keine Personen gesperrt.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    msg = ""
    for id in data.data["locked"]:
        msg += f"<@{id}>\n"

    embed = discord.Embed(color = 0xf2aa0d)
    embed.add_field(name = "Gesperrte Spieler:", value = msg, inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "team_liste", description = "Erstellt eine Liste von allen Teammitgliedern die stetig aktualisiert wird.")
async def team_liste(interaction: discord.Interaction, channel: discord.TextChannel):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    ids = [1003123527966269520, 1003123529102925895, 1003123530617081887, 1005167134726443138, 1003123531745349633, 1019621816148435036, 1003123519300833320, 1003123533821509682, 1003123534794608711, 1003125706575855636, 1015661709140181114]
    guild_obj = client.get_guild(1002128696360054794)

    msg = "Das Team:\n"

    for role in ids:
        role_obj = guild_obj.get_role(role)
        members = [x.id for x in role_obj.members]
        msg += f"\n<@&{role_obj.id}>\n"
        if len(members) == 0:
            msg += "-\n"
        for m in members:
            msg += f"- <@{m}>\n"

    m = await channel.send(content = msg)
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = "Die Teamliste wurde erfolgreich aufgesetzt!", inline = True)
    await interaction.response.send_message(embed = embed)
    
    data.data["loops"]["team_liste"]["channel"] = channel.id
    data.data["loops"]["team_liste"]["msg_id"] = m.id
    data.save()



# INVENTAR COMMANDS #



@client.tree.command(name = "item_erstellen", description = "Erstelle ein Item.")
async def item_erstellen(interaction: discord.Interaction, name: str, nachricht: str = None, platz: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if name.lower in [x.lower for x in data.data["items"].keys()]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Dieses Item ist bereits vorhanden!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if nachricht is None and platz is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib bei einem Item eine Nachricht an und bei einem Lager ein Platz!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if nachricht and platz:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib bei einem Item eine Nachricht an und bei einem Lager ein Platz!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if platz is None:
        data.create_item(name, nachricht)
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = "Das Item wurde erfolgreich erstellt!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if nachricht is None:
        if platz <= 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Bitte gib eine Zahl über 0 an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        data.create_storage(name, platz)
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = "Das Lager wurde erfolgreich erstellt!", inline = True)
        await interaction.response.send_message(embed = embed)


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "item_loeschen", description = "Danach kann das Item nicht mehr vergeben werden.")
async def item_loeschen(interaction: discord.Interaction, item: str):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item not in data.data["items"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Es gibt kein Item mit diesem Namen! Bitte achte auch auf groß- und kleinschreibung!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    del data.data["items"][item]
    # for k, v in data.data["item_log"].items():
    #     if v == item:
    #         del data.data["item_log"][k]

    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = "Das Item wurde erfolgreich gelöscht!", inline = True)
    await interaction.response.send_message(embed = embed)


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "item_geben", description = "Gibt einem Spieler Items. Diese werden neu erstellt.")
async def item_geben(interaction: discord.Interaction, besitzer: discord.Member, item: str, menge: int):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item not in data.data["items"]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"Es gibt kein Item namens {item}! Bitte achte auch auf groß- und kleinschreibung!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib eine Zahl über 0 an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(data.data["character"][besitzer.id]["inv"]) >= 25:
        name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"In dem Inventar von {name} ist kein platz mehr für die Gegenstände!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(data.data["character"][besitzer.id]["inv"]) + menge > 25:
        if isinstance(data.data["items"][item], str):
            while len(data.data["character"][besitzer.id]["inv"]) < 25:
                data.give_item(besitzer.id, item)
        else:
            while len(data.data["character"][besitzer.id]["inv"]) < 25:
                data.give_storage(besitzer.id, item)
        data.save()

        name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Das Inventar von {name} hatte nicht genug Platz für alle Gegenstände, deswegen wurde der vorhandene Platz aufgefüllt!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if isinstance(data.data["items"][item], str):
        for i in range(menge):
            data.give_item(besitzer.id, item)
    else:
        for i in range(menge):
            data.give_storage(besitzer.id, item)

    data.save()
    name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Die Items wurden erfolgreich in das Inventar von {name} gelegt!", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "inventar", description = "Zeigt ein Inventar eines Spielers.")
async def inventar(interaction: discord.Interaction, besitzer: discord.Member = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer:
        if besitzer.id not in data.data["character"].keys():
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        
        if len(data.data["character"][besitzer.id]["inv"]) == 0:
            embed = discord.Embed(color = 0xf2aa0d)
            embed.add_field(name = "Inventar", value = "Du hast keine Gegenstände in deinem Inventar!", inline = True)
            embed.set_footer(text = f"0/25 Gegenstände")
            await interaction.response.send_message(embed = embed)
            return
        
        inventar = data.data["character"][besitzer.id]["inv"]
        inventar_items = [x for x in inventar if x > 0]
        inventar_storages = [x for x in inventar if x < 0]

        # for i in inventar_items:
        #     if i not in data.data["item_log"]:
        #         data.data["character"][besitzer.id]["inv"].remove(i)

        inv_items = [data.data["item_log"][x] for x in inventar_items]
        inv_items_without_duplicate = list(set(inv_items))
        msg = ""
        for item in inv_items_without_duplicate:
            counter = inv_items.count(item)
            msg += f"{item} - {counter}x\n"

        for storage in inventar_storages:
            name = data.data["item_log"][storage]["name"]
            s_id = data.data["item_log"][storage]["id"]
            liste = data.data["item_log"][storage]["inv"]
            inv_items_s = [data.data["item_log"][x] for x in liste]
            inv_items_without_duplicate_s = list(set(inv_items_s))
            msg += f"{name}: ---------- *id:{s_id}*\n"

            for item in inv_items_without_duplicate_s:
                counter = inv_items_s.count(item)
                msg += f"-  {item} - {counter}x\n"

        l = len(data.data["character"][besitzer.id]["inv"])
        p_name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
        embed = discord.Embed(color = 0xf2aa0d)
        embed.add_field(name = f"Inventar von {p_name}", value = msg, inline = True)
        embed.set_footer(text = f"{l}/25 Gegenstände")
        await interaction.response.send_message(embed = embed)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Diese Person hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(data.data["character"][interaction.user.id]["inv"]) == 0:
        embed = discord.Embed(color = 0xf2aa0d)
        embed.add_field(name = "Inventar", value = "Du hast keine Gegenstände in deinem Inventar!", inline = True)
        embed.set_footer(text = f"0/25 Gegenstände")
        await interaction.response.send_message(embed = embed)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_items = [x for x in inventar if x > 0]
    inventar_storages = [x for x in inventar if x < 0]

    inv_items = [data.data["item_log"][x] for x in inventar_items]
    inv_items_without_duplicate = list(set(inv_items))
    msg = ""
    for item in inv_items_without_duplicate:
        counter = inv_items.count(item)
        msg += f"{item} - {counter}x\n"

    for storage in inventar_storages:
        name = data.data["item_log"][storage]["name"]
        s_id = data.data["item_log"][storage]["id"]
        liste = data.data["item_log"][storage]["inv"]
        inv_items_s = [data.data["item_log"][x] for x in liste]
        inv_items_without_duplicate_s = list(set(inv_items_s))
        msg += f"{name}: ---------- *id:{s_id}*\n"

        for item in inv_items_without_duplicate_s:
            counter = inv_items_s.count(item)
            msg += f"-  {item} - {counter}x\n"

    l = len(data.data["character"][interaction.user.id]["inv"])
    p_name = data.data["character"][interaction.user.id]["vor_name"] + " " + data.data["character"][interaction.user.id]["nach_name"]
    embed = discord.Embed(color = 0xf2aa0d)
    embed.add_field(name = f"Inventar von {p_name}", value = msg, inline = True)
    embed.set_footer(text = f"{l}/25 Gegenstände")
    await interaction.response.send_message(embed = embed)
    return


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "einpacken", description = "Legt Gegenstände in einen Container.")
async def inventar(interaction: discord.Interaction, id: int, item: str, menge: int):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib eine Menge über 0 an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_items = [x for x in inventar if x > 0]
    inventar_storages = [x for x in inventar if x < 0]
    item_names = []
    storage_ids = []
    storage_names = []

    for i in inventar_items:
        item_names.append(data.data["item_log"][i])

    for i in inventar_storages:
        storage_ids.append(data.data["item_log"][i]["id"])
        storage_names.append(data.data["item_log"][i]["name"])

    if id not in storage_ids:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du besitzt keinen Container mit dieser ID!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item in storage_names:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Kannst kein Container in einen Container packen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item not in item_names:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"Du besitzt kein Gegenstand names {item}!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    for i in inventar_storages:
        if data.data["item_log"][i]["id"] == id:
            storage = i
            break
        else: storage = None

    storage_name = data.data["item_log"][storage]["name"]
    storage_inv = data.data["item_log"][storage]["inv"]
    target_ids = []

    for i in inventar_items:
        if data.data["item_log"][i] == item:
            target_ids.append(i)

    if len(storage_inv) >= data.data["items"][storage_name]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Dieser Container ist voll!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item_names.count(item) < menge:
        n_menge = item_names.count(item)
        if len(storage_inv) + n_menge > data.data["items"][storage_name]:

            while len(data.data["item_log"][storage]["inv"]) < data.data["items"][storage_name]:
                removed_element = target_ids.pop(0)
                data.data["character"][interaction.user.id]["inv"].remove(removed_element)
                data.data["item_log"][storage]["inv"].append(removed_element)
            data.save()
            embed = discord.Embed(color = 0x61ff73)
            embed.add_field(name = "Erfolg", value = f"Der Container hatte nicht genug Platz für alle Gegenstände, deswegen wurde der vorhandene Platz aufgefüllt!", inline = True)
            await interaction.response.send_message(embed = embed)
            return

        for i in range(n_menge):
            removed_element = target_ids.pop(0)
            data.data["character"][interaction.user.id]["inv"].remove(removed_element)
            data.data["item_log"][storage]["inv"].append(removed_element)
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Es wurden {n_menge} Gegenstände in den Container gelegt.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if len(storage_inv) + menge > data.data["items"][storage_name]:

        while len(data.data["item_log"][storage]["inv"]) < data.data["items"][storage_name]:
            removed_element = target_ids.pop(0)
            data.data["character"][interaction.user.id]["inv"].remove(removed_element)
            data.data["item_log"][storage]["inv"].append(removed_element)
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Der Container hatte nicht genug Platz für alle Gegenstände, deswegen wurde der vorhandene Platz aufgefüllt!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    for i in range(menge):
        removed_element = target_ids.pop(0)
        data.data["character"][interaction.user.id]["inv"].remove(removed_element)
        data.data["item_log"][storage]["inv"].append(removed_element)
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Es wurden alle Gegenstände in den Container gelegt.", inline = True)
    await interaction.response.send_message(embed = embed)
    return


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "auspacken", description = "Holt Gegenstände aus einem Container.")
async def inventar(interaction: discord.Interaction, id: int, item: str, menge: int):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib eine Menge über 0 an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_items = [x for x in inventar if x > 0]
    inventar_storages = [x for x in inventar if x < 0]
    item_names = []
    storage_ids = []
    storage_names = []

    for i in inventar_items:
        item_names.append(data.data["item_log"][i])

    for i in inventar_storages:
        storage_ids.append(data.data["item_log"][i]["id"])
        storage_names.append(data.data["item_log"][i]["name"])

    if id not in storage_ids:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du besitzt keinen Container mit dieser ID!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    for i in inventar_storages:
        if data.data["item_log"][i]["id"] == id:
            storage = i
            break
        else: storage = None

    storage_inv = data.data["item_log"][storage]["inv"]
    target_ids = []

    for i in storage_inv:
        if data.data["item_log"][i] == item:
            target_ids.append(i)

    if len(inventar) >= 25:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Dein Inventar ist voll!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(target_ids) == 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"In diesem Container ist kein Gegenstand names {item}!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if len(target_ids) < menge:
        n_menge = len(target_ids)
        if len(inventar) + n_menge > 25:

            while len(data.data["character"][interaction.user.id]["inv"]) < 25:
                removed_element = target_ids.pop(0)
                data.data["item_log"][storage]["inv"].remove(removed_element)
                data.data["character"][interaction.user.id]["inv"].append(removed_element)
            data.save()
            embed = discord.Embed(color = 0x61ff73)
            embed.add_field(name = "Erfolg", value = f"Dein Inventar hatte nicht genug Platz für alle Gegenstände, deswegen wurde der vorhandene Platz aufgefüllt!", inline = True)
            await interaction.response.send_message(embed = embed)
            return

        for i in range(n_menge):
            removed_element = target_ids.pop(0)
            data.data["item_log"][storage]["inv"].remove(removed_element)
            data.data["character"][interaction.user.id]["inv"].append(removed_element)
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Es wurden {n_menge} Gegenstände in dein Inventar gelegt.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    if len(inventar) + menge > 25:

        while len(data.data["character"][interaction.user.id]["inv"]) < 25:
            removed_element = target_ids.pop(0)
            data.data["item_log"][storage]["inv"].remove(removed_element)
            data.data["character"][interaction.user.id]["inv"].append(removed_element)
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Dein Inventar hatte nicht genug Platz für alle Gegenstände, deswegen wurde der vorhandene Platz aufgefüllt!", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    for i in range(menge):
        removed_element = target_ids.pop(0)
        data.data["item_log"][storage]["inv"].remove(removed_element)
        data.data["character"][interaction.user.id]["inv"].append(removed_element)
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Es wurden alle Gegenstände in dein Inventar gelegt.", inline = True)
    await interaction.response.send_message(embed = embed)
    return


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "benutze", description = "Benutzt gegenstände. Diese werden danach aufgebraucht.")
async def inventar(interaction: discord.Interaction, item: str, menge: int):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge <= 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Bitte gib eine Menge über 0 an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_items = [x for x in inventar if x > 0]

    target_ids = []

    for i in inventar_items:
        if data.data["item_log"][i] == item:
            target_ids.append(i)

    if len(target_ids) == 0:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"Du besitzt kein Gegenstand names {item}!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item == "Ausweis":
        if exists(f"/home/pi/ausweise/{str(interaction.user.id)}.png"):
            await interaction.response.send_message(file = discord.File(f"/home/pi/ausweise/{str(interaction.user.id)}.png"))
            return
        else:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Du hast keinen Personalausweis!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

    if len(target_ids) < menge:
        n_menge = len(target_ids)
        for i in range(n_menge):
            removed_element = target_ids.pop(0)
            data.data["character"][interaction.user.id]["inv"].remove(removed_element)
            del data.data["item_log"][removed_element]
        data.save()
        msg = data.data["items"][item]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Da du nur {n_menge} Gegenstände hast wurden nur so viele benutzt:\n**{msg}**", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    for i in range(menge):
        removed_element = target_ids.pop(0)
        data.data["character"][interaction.user.id]["inv"].remove(removed_element)
        del data.data["item_log"][removed_element]
    data.save()
    msg = data.data["items"][item]
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"**{msg}**", inline = True)
    await interaction.response.send_message(embed = embed)
    return


@client.tree.command(name = "item_liste", description = "Zeigt dir alle Gegenstände und Container die es derzeit im spiel gibt.")
async def item_liste(interaction: discord.Interaction):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    items = ""
    container = ""
    for k, v in data.data["items"].items():
        if isinstance(v, str):
            items += k + "\n"
        else:
            container += k + f" ({str(v)})" + "\n"

    embed = discord.Embed(color = 0xf2aa0d)
    embed.add_field(name = "Gegenstände:", value = items, inline = False)
    embed.add_field(name = "Container:", value = container, inline = False)
    await interaction.response.send_message(embed = embed)


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "wegwerfen", description = "Lösche gegenstände.")
async def wegwerfen(interaction: discord.Interaction, item: str = None, menge: int = None, id: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge is None and item is None and id is None:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

    if not menge is None and not item is None and not id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if id is None:

        if menge <= 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Bitte gib eine Menge über 0 an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        inventar = data.data["character"][interaction.user.id]["inv"]
        inventar_items = [x for x in inventar if x > 0]

        target_ids = []

        for i in inventar_items:
            if data.data["item_log"][i] == item:
                target_ids.append(i)

        if len(target_ids) == 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = f"Du besitzt kein Gegenstand names {item}!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if len(target_ids) < menge:
            n_menge = len(target_ids)
            for i in range(n_menge):
                removed_element = target_ids.pop(0)
                data.data["character"][interaction.user.id]["inv"].remove(removed_element)
                del data.data["item_log"][removed_element]
            data.save()
            embed = discord.Embed(color = 0x61ff73)
            embed.add_field(name = "Erfolg", value = f"Da du nur {n_menge} Gegenstände hast, wurden nur so viele gelöscht.", inline = True)
            await interaction.response.send_message(embed = embed)
            return

        for i in range(menge):
            removed_element = target_ids.pop(0)
            data.data["character"][interaction.user.id]["inv"].remove(removed_element)
            del data.data["item_log"][removed_element]
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Alle Gegenstände wurden erfolgreich gelöscht.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_storages = [x for x in inventar if x < 0]
    id *= -1 

    if id not in inventar_storages:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"In deinem Inventar wurde kein Container mit der ID {id} gefunden!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    data.data["character"][interaction.user.id]["inv"].remove(id)
    del data.data["item_log"][id]
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = "Der Container wurde erfolgreich gelöscht!", inline = True)
    await interaction.response.send_message(embed = embed)


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "nehmen", description = "Nimmt Gegenstände von einem Spieler und legt sie in dein Inventar.")
async def nehmen(interaction: discord.Interaction, besitzer: discord.Member, item: str = None, menge: int = None, id: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return
        
    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Dieses Mitglied hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge is None and item is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if not menge is None and not item is None and not id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if id is None:
        if menge <= 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Bitte gib eine Menge über 0 an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if len(data.data["character"][interaction.user.id]["inv"]) + menge > 25:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "In dein Inventar passt nicht so viel rein!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        inventar = data.data["character"][besitzer.id]["inv"]
        inventar_items = [x for x in inventar if x > 0]

        target_ids = []

        for i in inventar_items:
            if data.data["item_log"][i] == item:
                target_ids.append(i)

        if len(target_ids) == 0:
            name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = f"{name} besitzt kein Gegenstand names {item}!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if len(target_ids) < menge:
            n_menge = len(target_ids)
            for i in range(n_menge):
                removed_element = target_ids.pop(0)
                data.data["character"][besitzer.id]["inv"].remove(removed_element)
                data.data["character"][interaction.user.id]["inv"].append(removed_element)
            data.save()
            name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
            embed = discord.Embed(color = 0x61ff73)
            embed.add_field(name = "Erfolg", value = f"Da {name} nur {n_menge} Gegenstände hat, konnten nur so viele in dein Inventar gelegt werden.", inline = True)
            await interaction.response.send_message(embed = embed)
            return

        for i in range(menge):
            removed_element = target_ids.pop(0)
            data.data["character"][besitzer.id]["inv"].remove(removed_element)
            data.data["character"][interaction.user.id]["inv"].append(removed_element)
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Alle Gegenstände wurden erfolgreich in dein Inventar gelegt.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    inventar = data.data["character"][besitzer.id]["inv"]
    inventar_storages = [x for x in inventar if x < 0]
    id *= -1 

    if id not in inventar_storages:
        name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"In dem Inventar von {name} wurde kein Container mit der ID {id} gefunden!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return
    
    data.data["character"][besitzer.id]["inv"].remove(id)
    data.data["character"][interaction.user.id]["inv"].append(id)
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = "Der Container wurde dir erfolgreich übergeben!", inline = True)
    await interaction.response.send_message(embed = embed)


@app_commands.autocomplete(item = item_autocompletion)
@client.tree.command(name = "geben", description = "Gibt einem Spieler Gegenstände aus deinem Inventar.")
async def geben(interaction: discord.Interaction, besitzer: discord.Member, item: str = None, menge: int = None, id: int = None):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return
        
    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if besitzer.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Dieses Mitglied hat keinen Charakter!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge is None and item is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if not menge is None and not item is None and not id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if menge is None and id is None:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Entweder gibst du die ID des Containers an oder du gibst den Namen und eine Mengen von einem Item an!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if id is None:
        if menge <= 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = "Bitte gib eine Menge über 0 an!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if len(data.data["character"][besitzer.id]["inv"]) + menge > 25:
            name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = f"In das Inventar von {name} passt nicht so viel rein!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        inventar = data.data["character"][interaction.user.id]["inv"]
        inventar_items = [x for x in inventar if x > 0]

        target_ids = []

        for i in inventar_items:
            if data.data["item_log"][i] == item:
                target_ids.append(i)

        if len(target_ids) == 0:
            embed = discord.Embed(color = 0xfe4d4d)
            embed.add_field(name = "Fehler", value = f"Du besitzt kein Gegenstand names {item}!", inline = True)
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return

        if len(target_ids) < menge:
            n_menge = len(target_ids)
            for i in range(n_menge):
                removed_element = target_ids.pop(0)
                data.data["character"][interaction.user.id]["inv"].remove(removed_element)
                data.data["character"][besitzer.id]["inv"].append(removed_element)
            data.save()
            name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
            embed = discord.Embed(color = 0x61ff73)
            embed.add_field(name = "Erfolg", value = f"Da du nur {n_menge} Gegenstände hast, konntest du {name} nur so viele geben.", inline = True)
            await interaction.response.send_message(embed = embed)
            return

        for i in range(menge):
            removed_element = target_ids.pop(0)
            data.data["character"][interaction.user.id]["inv"].remove(removed_element)
            data.data["character"][besitzer.id]["inv"].append(removed_element)
        data.save()
        name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Alle Gegenstände wurden erfolgreich in das Inventar von {name} gelegt.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_storages = [x for x in inventar if x < 0]
    id *= -1 

    if id not in inventar_storages:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"In deinem Inventar wurde kein Container mit der ID {id} gefunden!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return
    
    data.data["character"][interaction.user.id]["inv"].remove(id)
    data.data["character"][besitzer.id]["inv"].append(id)
    data.save()
    name = data.data["character"][besitzer.id]["vor_name"] + " " + data.data["character"][besitzer.id]["nach_name"]
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Der Container wurde erfolgreich an {name} übergeben!", inline = True)
    await interaction.response.send_message(embed = embed)



# FARMING UND CRAFTING #



# Noch Items erstellen
@client.tree.command(name = "farm", description = "Mit diesem Befehl kannst du verschiedene sachen Farmen.")
@app_commands.choices(route = [
    Choice(name = "Stein", value = "Bruchstein"),
    Choice(name = "Holz", value = "Baumstamm"),
    Choice(name = "Wein", value = "Weintrauben"),
    Choice(name = "Zitrone", value = "Zitrone"),
    Choice(name = "Tabak", value = "Tabakpflanze"),
    Choice(name = "Kokain", value = "Kokapflanze"),
    Choice(name = "Weed", value = "Weedpflanze")
])
async def farm(interaction: discord.Interaction, route: Choice[str]):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id in data.data["loops"]["farming"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du farmst oder craftest gerade etwas anderes!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Bruchstein" and not interaction.channel.id == 1003123875950891008:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Baumstamm" and not interaction.channel.id == 1003123881151823972:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Weintrauben" and not interaction.channel.id == 1003123887124512831:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Zitrone" and not interaction.channel.id == 1003123892841349300:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Tabakpflanze" and not interaction.channel.id == 1003123901129293935:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Kokapflanze" and not interaction.channel.id == 1003123908133793912:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Weedpflanze" and not interaction.channel.id == 1003123914022584410:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_items = [x for x in inventar if x > 0]
    inv_items = [data.data["item_log"][x] for x in inventar_items]
    inv_items_without_duplicate = list(set(inv_items))

    if route.value == "Bruchstein" and not "Spitzhacke" in inv_items_without_duplicate:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst eine Spitzhacke um Stein zu farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value == "Baumstamm" and not "Axt" in inv_items_without_duplicate:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst eine Axt um Holz zu farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if not "Schere" in inv_items_without_duplicate and not route.value in ["Baumstamm", "Bruchstein"]:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = f"Du brauchst eine Schere um {route.name} zu farmen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if route.value in ["Kokapflanze", "Weedpflanze"]:
        end_time_dt_obj = datetime.datetime.now() + datetime.timedelta(minutes = 15)
        time_stamp = end_time_dt_obj.timestamp()
        data.data["loops"]["farming"][interaction.user.id] = {
            "end": time_stamp,
            "item": route.value,
            "menge": 20
        }
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Du wirst deine Gegenstände in 15 Minuten erhalten!\nAchte bitte darauf, dass du genug platz im Inventar hast, ansonsten werden dir nicht alle Gegenstände gegeben.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    end_time_dt_obj = datetime.datetime.now() + datetime.timedelta(minutes = 10)
    time_stamp = end_time_dt_obj.timestamp()
    data.data["loops"]["farming"][interaction.user.id] = {
        "end": time_stamp,
        "item": route.value,
        "menge": 15
    }
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Du wirst deine Gegenstände in 10 Minuten erhalten!\nAchte bitte darauf, dass du genug platz im Inventar hast, ansonsten werden dir nicht alle Gegenstände gegeben.", inline = True)
    await interaction.response.send_message(embed = embed)


@client.tree.command(name = "craft", description = "Mit diesem Befehl kannst du verschiedene sachen Craften.")
@app_commands.choices(item = [
    Choice(name = "Stein", value = "Stein"),
    Choice(name = "Brett", value = "Brett"),
    Choice(name = "Wein", value = "Wein"),
    Choice(name = "Limonade", value = "Limonade"),
    Choice(name = "Tabak", value = "Tabak"),
    Choice(name = "Kokain", value = "Kokain"),
    Choice(name = "Weed", value = "Weed")
])
async def craft(interaction: discord.Interaction, item: Choice[str]):

    if interaction.user.id in data.data["locked"]:
        embed = discord.Embed(color = 0xc20000)
        embed.add_field(name = "Fehler", value = "Du wurdest von einem Admin gesperrt! Wenn du denkst, dass dies ein Fehler ist, dann schreibe ein Teammitglied Privat an.", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id not in data.data["character"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst einen Charakter um diesen Befehl zu benutzen!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if interaction.user.id in data.data["loops"]["farming"].keys():
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du farmst oder craftest gerade etwas anderes!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Stein" and not interaction.channel.id == 1003123877272092672:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Brett" and not interaction.channel.id == 1003123882313646081:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Wein" and not interaction.channel.id == 1003123888668037170:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Limonade" and not interaction.channel.id == 1003123894212907020:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Tabak" and not interaction.channel.id == 1003123902572150894:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Kokain" and not interaction.channel.id == 1003123909715034183:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Weed" and not interaction.channel.id == 1003123915373166722:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du kannst das nicht in dem Channel craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    inventar = data.data["character"][interaction.user.id]["inv"]
    inventar_items = [x for x in inventar if x > 0]
    inv_items = [data.data["item_log"][x] for x in inventar_items]

    if item.value == "Stein" and inv_items.count("Bruchstein") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Materialien um diesen Gegenstand zu Craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Brett" and inv_items.count("Baumstamm") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Materialien um diesen Gegenstand zu Craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Wein" and inv_items.count("Weintrauben") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Materialien um diesen Gegenstand zu Craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Limonade" and inv_items.count("Zitrone") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Materialien um diesen Gegenstand zu Craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Tabak" and inv_items.count("Tabakpflanze") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Materialien um diesen Gegenstand zu Craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Kokain" and inv_items.count("Kokapflanze") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du hast nicht genug Materialien um diesen Gegenstand zu Craften!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value == "Weed" and inv_items.count("Weedpflanze") < 5:
        embed = discord.Embed(color = 0xfe4d4d)
        embed.add_field(name = "Fehler", value = "Du brauchst eine Spitzhacke um Stein zu crafte!", inline = True)
        await interaction.response.send_message(embed = embed, ephemeral = True)
        return

    if item.value in ["Kokain", "Weed"]:
        target_ids = []

        if item.value == "Kokain": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Kokapflanze":
                    target_ids.append(i)
        if item.value == "Weed": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Weedpflanze":
                    target_ids.append(i)
        for i in range(5):
            removed_element = target_ids.pop(0)
            data.data["character"][interaction.user.id]["inv"].remove(removed_element)
            del data.data["item_log"][removed_element]
        data.save()

        end_time_dt_obj = datetime.datetime.now() + datetime.timedelta(minutes = 5)
        time_stamp = end_time_dt_obj.timestamp()
        data.data["loops"]["farming"][interaction.user.id] = {
            "end": time_stamp,
            "item": item.value,
            "menge": 20
        }
        data.save()
        embed = discord.Embed(color = 0x61ff73)
        embed.add_field(name = "Erfolg", value = f"Du wirst deine Gegenstände in 15 Minuten erhalten!\nAchte bitte darauf, dass du genug platz im Inventar hast, ansonsten werden dir nicht alle Gegenstände gegeben.", inline = True)
        await interaction.response.send_message(embed = embed)
        return

    target_ids = []
    if item.value == "Stein": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Bruchstein":
                    target_ids.append(i)
    if item.value == "Brett": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Baumstamm":
                    target_ids.append(i)
    if item.value == "Wein": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Weintrauben":
                    target_ids.append(i)
    if item.value == "Limonade": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Zitrone":
                    target_ids.append(i)
    if item.value == "Tabak": 
            for i in inventar_items:
                if data.data["item_log"][i] == "Tabakpflanze":
                    target_ids.append(i)
    for i in range(5):
        removed_element = target_ids.pop(0)
        data.data["character"][interaction.user.id]["inv"].remove(removed_element)
        del data.data["item_log"][removed_element]
    data.save()
    end_time_dt_obj = datetime.datetime.now() + datetime.timedelta(minutes = 2)
    time_stamp = end_time_dt_obj.timestamp()
    data.data["loops"]["farming"][interaction.user.id] = {
        "end": time_stamp,
        "item": item.value,
        "menge": 15
    }
    data.save()
    embed = discord.Embed(color = 0x61ff73)
    embed.add_field(name = "Erfolg", value = f"Du wirst deine Gegenstände in 10 Minuten erhalten!\nAchte bitte darauf, dass du genug platz im Inventar hast, ansonsten werden dir nicht alle Gegenstände gegeben.", inline = True)
    await interaction.response.send_message(embed = embed)



# LOOP #



@tasks.loop(seconds = 30)
async def loop():
    if not data.data["loops"]["team_liste"]["channel"] is None:
        ids = [1003123527966269520, 1003123529102925895, 1003123530617081887, 1005167134726443138, 1003123531745349633, 1019621816148435036, 1003123519300833320, 1003123533821509682, 1003123534794608711, 1003125706575855636, 1015661709140181114]
        guild_obj = client.get_guild(1002128696360054794)

        msg = "Hier ist die Aktuelle Teamaufstellung:\n"

        for role in ids:
            role_obj = guild_obj.get_role(role)
            members = [x.id for x in role_obj.members]
            msg += f"\n<@&{role_obj.id}>\n"
            if len(members) == 0:
                msg += "-\n"
            for m in members:
                msg += f"- <@{m}>\n"

        c = client.get_channel(data.data["loops"]["team_liste"]["channel"])
        m = await c.fetch_message(data.data["loops"]["team_liste"]["msg_id"])
        await m.edit(content = msg)

    for k, v in data.data["loops"]["farming"].items():
        if v["end"] >= datetime.datetime.now().timestamp():

            if len(data.data["character"][k]["inv"]) + v["menge"] > 25:
                while len(data.data["character"][k]["inv"]) < 25:
                    data.give_item(k, v["item"])
                del data.data["loops"]["farming"][k]
                data.save()
                return

            for _ in range(v["menge"]):
                data.give_item(k, v["item"])
            del data.data["loops"]["farming"][k]
            data.save()

client.run(variable("bot_key"))
