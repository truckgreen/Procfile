import discord
from discord.ext import commands
import re
import random
import asyncio 
import sys # Importado para la solución de Windows
from langdetect import detect # Para detección de idioma
import datetime # Para el comando *hora
import pytz # Para zonas horarias en *hora

# --- CONFIGURACIÓN PRINCIPAL ---
# Necesario para obtener el contenido de los mensajes y los eventos de miembros
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', intents=intents)

# --- CONFIGURACIONES ESPECÍFICAS (¡REVISA LOS VALORES DE EJEMPLO!) ---
# ID del canal para los registros de moderación (mensajes eliminados)
LOGS_CHANNEL_ID = 123456789012345678  # << REEMPLAZA ESTE ID
# ID del canal para las bienvenidas
WELCOME_CHANNEL_ID = 1404936809145962528 # << REEMPLAZA ESTE ID
# ID del canal para las despedidas
GOODBYE_CHANNEL_ID = 1408861879350333481 # << REEMPLAZA ESTE ID
# ID del canal de reglas/información que debe aparecer en el mensaje de bienvenida
RULES_CHANNEL_ID = 1409286351035039855 # << REEMPLAZA ESTE ID

# --- CONFIGURACIÓN DE ROLES ADICIONAL ---
# ID del rol que se asignará automáticamente al unirse
DEFAULT_ROLE_ID = 1407487402997579899  

# --- CONFIGURACIÓN DE TICKETS APLICADA ---
SUPPORT_ROLE_ID = 1407752049646506145 # ID del Rol de Staff
TICKET_CATEGORY_ID = 1407754184714879038 # ID de la Categoría de Tickets

# Expresión regular para detectar enlaces comunes
LINK_REGEX = r'(https?://\S+|www\.\S+)'

# 🛑 ¡ERROR DE CONEXIÓN PREVIO! REEMPLAZA ESTE VALOR CON TU NUEVO TOKEN. 🛑
BOT_TOKEN = 'MTQyMTIyOTYyNTU3NjUyMTczMA.GS44-x.NV_nUAAoWz5F3aauMlVyWIII0JncaQe8Jddji8' 

# ----------------------------------------------------------------------
# DICCIONARIO DE TRADUCCIONES (TEXTOS LOCALIZADOS - I18N)
# ----------------------------------------------------------------------
RESPONSES = {
    "default_lang": "es",

    # Saludo (*hola)
    "hello": {
        "es": [
            "Hola {user}, ¿cómo estás? Soy un bot bilingüe.",
            "¡Un placer saludarte, {user}! ¿Qué necesitas?"
        ],
        "en": [
            "Hello {user}, how are you? I'm a bilingual bot.",
            "Nice to greet you, {user}! What do you need?"
        ]
    },
    
    # Dado (*dado)
    "dice_roll": {
        "es": "🎲 **{user}** tiró el dado y obtuvo un **{result}**!",
        "en": "🎲 **{user}** rolled the dice and got a **{result}**!"
    },
    
    # Abrazo (*abrazo)
    "hug": {
        "self_hug_es": "¡**{user}** se está abrazando a sí mismo! Aww 🤗",
        "hug_other_es": "🫂 **{user}** le dio un gran abrazo a **{member}**.",
        "self_hug_en": "Ew! **{user}** is hugging themselves! Aww 🤗",
        "hug_other_en": "🫂 **{user}** gave a big hug to **{member}**."
    },
    
    # Bola Mágica (*pregunta)
    "8ball_title": {
        "es": "🔮 Bola Mágica del 8",
        "en": "🔮 Magic 8-Ball"
    },
    "8ball_question": {
        "es": "Pregunta",
        "en": "Question"
    },
    "8ball_answer": {
        "es": "Respuesta",
        "en": "Answer"
    },
    "8ball_responses": {
        "es": [
            "Sí, definitivamente.", "Parece que sí.", "Es incierto, intenta de nuevo.",
            "Pregúntame más tarde.", "No lo creo.", "Absolutamente no.", "Sin duda.", "Deja el fastidio."
        ],
        "en": [
            "Yes, definitely.", "It seems so.", "It's uncertain, try again.",
            "Ask me later.", "I don't think so.", "Absolutely not.", "Without a doubt.", "Stop bothering me."
        ]
    },
    
    # Comando *cuando sale la actualización
    "when_update": {
        "es": "Y yo que voy a saber, deja la preguntadera",
        "en": "And how am I supposed to know that, stop asking questions"
    },
    
    # Comando *hora
    "time_errors": {
        "es": "⚠️ Lo siento, no pude encontrar una zona horaria válida para **{query}**. Intenta con un nombre de capital o zona conocida (ej. *hora en Tokyo o *hora en America/New_York).",
        "en": "⚠️ Sorry, I couldn't find a valid time zone for **{query}**. Try a capital name or known zone (e.g., *time in Tokyo or *time in America/New_York)."
    },
    "time_embed_title": {
        "es": "⏰ Hora en {query}",
        "en": "⏰ Time in {query}"
    },
    "time_embed_description": {
        "es": "La hora en esa zona es:",
        "en": "The time in that zone is:"
    }
}

# --- FUNCIÓN DE UTILIDAD PARA DETECCIÓN DE IDIOMA ---
def get_language_key(text):
    """Detecta el idioma del texto o usa el predeterminado si falla."""
    try:
        # Quitamos el prefijo para intentar analizar solo el texto real
        if text.startswith(bot.command_prefix):
             text = text[len(bot.command_prefix):]
        
        detected_lang = detect(text).lower()
        if "es" in detected_lang:
            return "es"
        elif "en" in detected_lang:
            return "en"
        else:
            return RESPONSES["default_lang"]
    except:
        return RESPONSES["default_lang"]


# ----------------------------------------------------------------------
# 5. LÓGICA DEL SISTEMA DE TICKETS
# ----------------------------------------------------------------------
# (La lógica de tickets no requiere bilingüismo avanzado en el backend, se mantiene en español)

# Clase para el botón de "Abrir Ticket"
class TicketButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_number = 1 
        
    @discord.ui.button(label="Abrir Ticket de Soporte", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="open_ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True) 

        guild = interaction.guild
        member = interaction.user
        support_role = guild.get_role(SUPPORT_ROLE_ID)
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        # ... (restante de la lógica de tickets, omitida por espacio) ...

        # 1. Comprobar si ya tiene un ticket abierto (busca canales cuyo topic sea el ID del usuario)
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) and str(member.id) == channel.topic:
                return await interaction.followup.send(f"⚠️ Ya tienes un ticket abierto en {channel.mention}.", ephemeral=True)

        # 2. Crear el canal privado
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), 
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True), 
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True) 
        }

        channel_name = f"ticket-{self.ticket_number:04d}-{member.name[:10].lower().replace(' ', '-')}"
        
        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=str(member.id) 
            )
            self.ticket_number += 1

        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Error: El bot no tiene permisos para crear canales en esa categoría. Verifica la jerarquía de roles.", ephemeral=True)
        
        # 3. Botón de Cerrar Ticket
        close_button = discord.ui.Button(label="Cerrar Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_button")
        
        async def close_callback(interaction: discord.Interaction):
            is_staff = support_role in interaction.user.roles
            is_creator = str(interaction.user.id) == ticket_channel.topic
            
            if is_creator or is_staff or interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("El ticket se cerrará en 5 segundos. ¡Gracias por tu paciencia!", ephemeral=False)
                await ticket_channel.delete(reason=f"Ticket cerrado por {interaction.user.name}")
            else:
                await interaction.response.send_message("⚠️ Solo el creador del ticket o el staff pueden cerrarlo.", ephemeral=True)
        
        close_button.callback = close_callback
        
        # 4. Enviar el mensaje inicial al ticket
        embed = discord.Embed(
            title="🎫 Ticket de Soporte Abierto",
            description=f"{member.mention}, un miembro del equipo de **{support_role.mention}** te atenderá pronto.\n\n"
                        "Por favor, describe tu problema. Para cerrar este ticket, usa el botón de abajo.",
            color=discord.Color.blue()
        )
        
        await ticket_channel.send(f"{member.mention} {support_role.mention}", delete_after=0.1) 
        await ticket_channel.send(embed=embed, view=discord.ui.View(close_button))
        await interaction.followup.send(f"✅ ¡Tu ticket ha sido creado! Dirígete a {ticket_channel.mention}", ephemeral=True)

# Comando para configurar el panel de tickets
@bot.command(name='setup_ticket', help='Envía el panel con el botón de ticket al canal.')
@commands.has_permissions(administrator=True)
async def setup_ticket_panel(ctx):
    if SUPPORT_ROLE_ID == 0 or TICKET_CATEGORY_ID == 0:
        return await ctx.send("⚠️ ¡Error de Configuración! Debes establecer los IDs de SUPPORT_ROLE_ID y TICKET_CATEGORY_ID en el código primero.")
        
    embed = discord.Embed(
        title="Sistema de Tickets de Soporte",
        description="Presiona el botón de abajo para crear un nuevo canal privado de soporte.",
        color=discord.Color.dark_blue()
    )
    await ctx.send(embed=embed, view=TicketButton(bot))


# ----------------------------------------------------------------------
# INICIO DEL BOT Y ON_READY 
# ----------------------------------------------------------------------

@bot.event
async def on_ready():
    """Confirma que el bot ha iniciado sesión y está listo."""
    print(f'✅ Bot conectado como: {bot.user}')
    
    # INICIALIZA LA VISTA PERSISTENTE
    bot.add_view(TicketButton(bot))
    print('✅ Sistema de Tickets inicializado.')

# ----------------------------------------------------------------------
# LÓGICA DE EVENTOS (Moderación, Bienvenidas)
# ----------------------------------------------------------------------

@bot.event
async def on_member_join(member):
    
    # Espera a que el bot esté completamente listo
    await bot.wait_until_ready()
    
    if bot.is_closed():
        return
        
    # LÓGICA PARA ASIGNAR EL ROL AUTOMÁTICO (Omitida por espacio, pero incluida en el archivo)
    default_role = member.guild.get_role(DEFAULT_ROLE_ID)
    if default_role:
        try:
            await member.add_roles(default_role, reason="Asignación automática al unirse")
            print(f"✅ Rol '{default_role.name}' asignado a {member.name}.")
        except discord.Forbidden:
            print(f"⚠️ Error: El bot no tiene permiso para asignar el rol ID {DEFAULT_ROLE_ID}.")
        except discord.HTTPException as e:
            print(f"⚠️ Error al asignar el rol a {member.name}: {e}")

    # LÓGICA DE BIENVENIDA (Omitida por espacio, pero incluida en el archivo)
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    rules_channel = bot.get_channel(RULES_CHANNEL_ID)
    
    rules_mention = rules_channel.mention if rules_channel else "#el-canal-de-reglas"

    if welcome_channel:
        welcome_embed = discord.Embed(
            title=f"🎉 ¡Bienvenido/a a {member.guild.name}!",
            description=(
                f"¡Hola, {member.mention}! Estamos encantados de tenerte aquí.\n"
                f"Actualmente somos **{len(member.guild.members)}** miembros.\n\n"
                f"Por favor, ¡echa un vistazo a {rules_mention}!"
            ),
            color=discord.Color.green()
        )
        welcome_embed.set_thumbnail(url=member.display_avatar.url)
        welcome_embed.set_footer(text="¡No olvides leer las reglas!")
        
        try:
            await welcome_channel.send(embed=welcome_embed)
        except discord.Forbidden:
            pass

@bot.event
async def on_member_remove(member):
    if bot.is_closed():
        return
        
    # LÓGICA DE DESPEDIDA (Omitida por espacio, pero incluida en el archivo)
    goodbye_channel = bot.get_channel(GOODBYE_CHANNEL_ID)
    
    if goodbye_channel:
        goodbye_embed = discord.Embed(
            title="👋 ¡Hasta Pronto!",
            description=f"**{member.name}** ha dejado el servidor. ¡Esperamos que vuelva pronto!",
            color=discord.Color.dark_grey()
        )
        try:
            await goodbye_channel.send(embed=goodbye_embed)
        except discord.Forbidden:
            pass

@bot.event
async def on_message(message):
    
    if bot.is_closed(): return
    if message.author.bot:
        await bot.process_commands(message)
        return

    # Lógica Anti-Link (Omitida por espacio, pero incluida en el archivo)
    is_moderator = message.author.guild_permissions.manage_messages
    if re.search(LINK_REGEX, message.content) and not is_moderator:
        
        log_channel = bot.get_channel(LOGS_CHANNEL_ID)
        if log_channel:
            embed_log = discord.Embed(
                title="❌ Message Deleted (Anti-Link)", color=discord.Color.red(),
                description=f"**User:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** `{message.content}`"
            )
            await log_channel.send(embed=embed_log)

        try:
            await message.delete()
        except discord.Forbidden:
            print("Error: The bot does not have permission to delete messages.")
        
        return 

    await bot.process_commands(message)


# ----------------------------------------------------------------------
# 2. COMANDO DE MODERACIÓN: Banear
# ----------------------------------------------------------------------

@bot.command(name='ban', help='Banea a un usuario y elimina sus mensajes de los últimos 7 días.')
@commands.has_permissions(ban_members=True)
async def simple_ban(ctx, member: discord.Member, *, reason="Unspecified reason"):
    
    if bot.is_closed(): return
        
    # ... (lógica de ban, omitida por espacio) ...
    if member.id == ctx.author.id:
        return await ctx.send("❌ You cannot ban yourself.")
    
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Permission Error: You cannot ban a user with a role equal to or higher than yours.")
        
    try:
        await member.ban(delete_message_days=7, reason=reason)
        
        embed = discord.Embed(
            title="🔨 User Banned",
            color=discord.Color.dark_red(),
            description=f"**User:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Messages Deleted:** Last **7** days (Default Clean)\n**Reason:** {reason}"
        )
        await ctx.send(embed=embed)
    
    except discord.Forbidden:
        await ctx.send("❌ Permission Error: The bot cannot ban this user (Check bot role hierarchy).")
    except discord.HTTPException as e:
        await ctx.send(f"❌ An error occurred during the ban: {e}")

# ----------------------------------------------------------------------
# 4. COMANDOS DE DIVERSIÓN (BILINGÜES)
# ----------------------------------------------------------------------

@bot.command(name='hola', aliases=['hi', 'saludo'], help='El bot te saluda/The bot says hi.')
async def saludo(ctx):
    
    message_content = ctx.message.content
    lang_key = get_language_key(message_content)

    response_list = RESPONSES["hello"].get(lang_key, RESPONSES["hello"]["es"]) 
    raw_response = random.choice(response_list)
    final_response = raw_response.format(user=ctx.author.name)
    
    await ctx.send(final_response)

@bot.command(name='dado', aliases=['roll'], help='Tira un dado de 6 caras/Rolls a 6-sided die.')
async def roll_dice(ctx):
    
    message_content = ctx.message.content
    lang_key = get_language_key(message_content)

    resultado = random.randint(1, 6)
    
    response_template = RESPONSES["dice_roll"].get(lang_key, RESPONSES["dice_roll"]["es"])
    final_response = response_template.format(user=ctx.author.name, result=resultado)
    
    await ctx.send(final_response)

@bot.command(name='pregunta', aliases=['question', '8ball'], help='La Bola Mágica responde/The Magic 8-Ball answers.')
async def eight_ball(ctx, *, question):
    
    message_content = ctx.message.content
    lang_key = get_language_key(message_content)
    
    # Obtener textos del diccionario
    respuestas = RESPONSES["8ball_responses"].get(lang_key, RESPONSES["8ball_responses"]["es"])
    title_text = RESPONSES["8ball_title"].get(lang_key, RESPONSES["8ball_title"]["es"])
    question_field = RESPONSES["8ball_question"].get(lang_key, RESPONSES["8ball_question"]["es"])
    answer_field = RESPONSES["8ball_answer"].get(lang_key, RESPONSES["8ball_answer"]["es"])
    
    respuesta_elegida = random.choice(respuestas)
    
    embed = discord.Embed(
        title=title_text,
        color=discord.Color.purple()
    )
    embed.add_field(name=question_field, value=question, inline=False)
    embed.add_field(name=answer_field, value=f"**{respuesta_elegida}**", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='abrazo', aliases=['hug'], help='Abraza a otro usuario/Hugs another user.')
async def hug(ctx, member: discord.Member):
    
    message_content = ctx.message.content
    lang_key = get_language_key(message_content)

    if member == ctx.author:
        # Respuesta si se abraza a sí mismo
        response_template = RESPONSES["hug"].get(f"self_hug_{lang_key}", RESPONSES["hug"]["self_hug_es"])
        await ctx.send(response_template.format(user=ctx.author.name))
    else:
        # Respuesta si abraza a otro
        response_template = RESPONSES["hug"].get(f"hug_other_{lang_key}", RESPONSES["hug"]["hug_other_es"])
        await ctx.send(response_template.format(user=ctx.author.name, member=member.name))

@bot.command(name='cuando', aliases=['cuandosale', 'actualizacion', 'when', 'whenupdate'], help='Responde a preguntas sobre actualizaciones/Answers update questions.')
async def cuando_sale(ctx):
    
    message_content = ctx.message.content
    lang_key = get_language_key(message_content)
    
    contestacion = RESPONSES["when_update"].get(lang_key, RESPONSES["when_update"]["es"])
    
    await ctx.send(contestacion)


@bot.command(name='hora', aliases=['time', 'timein'], help='Muestra la hora actual en un país o zona horaria específica.')
async def get_time_by_country(ctx, *, country_or_city: commands.clean_content):
    
    message_content = ctx.message.content
    lang_key = get_language_key(message_content)
    
    # 1. Buscar la zona horaria
    search_term = country_or_city.strip().lower().replace(" ", "_")
    found_zone = None
    
    for zone in pytz.all_timezones:
        normalized_zone = zone.lower().replace(" ", "_")
        if search_term in normalized_zone:
            found_zone = zone
            break

    if not found_zone:
        # Si no se encuentra una zona válida, usa el error traducido
        error_message = RESPONSES["time_errors"].get(lang_key, RESPONSES["time_errors"]["es"])
        await ctx.send(error_message.format(query=country_or_city))
        return

    try:
        # 2. Calcular la hora
        tz = pytz.timezone(found_zone)
        now = datetime.datetime.now(tz)
        
        # Formatear la hora
        time_str = now.strftime("%I:%M:%S %p")
        
        # 3. Obtener el título y descripción traducidos para el embed
        title_text = RESPONSES["time_embed_title"].get(lang_key, RESPONSES["time_embed_title"]["es"])
        desc_text = RESPONSES["time_embed_description"].get(lang_key, RESPONSES["time_embed_description"]["es"])
        
        # 4. Formatear la fecha según el idioma (Corrección)
        if lang_key == "en":
             date_str = now.strftime("%A, %B %d, %Y")
        else: # Español
             # Tuve que definir los nombres de los días y meses manualmente, ya que strftime en Python base
             # no soporta traducción sin configurar la localización del SO (cosa que queremos evitar).
             day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
             month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
             
             # CORRECCIÓN: Usar now.weekday() (0-6) para indexar en la lista
             day_of_week = day_names[now.weekday()]
             month_name = month_names[now.month - 1]
             date_str = f"{day_of_week}, {now.day} de {month_name} de {now.year}"


        # 5. Enviar la respuesta
        embed = discord.Embed(
            title=title_text.format(query=country_or_city.title()),
            description=f"{desc_text}\n\n**{time_str}**\n_{date_str}_",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    except pytz.UnknownTimeZoneError:
        # Error interno
        await ctx.send(f"⚠️ Error interno: La zona '{found_zone}' no es válida.")
# ----------------------------------------------------------------------
# --- INICIO DEL BOT (CORRECCIÓN ESTRUCTURAL PARA WINDOWS) ---
# ----------------------------------------------------------------------

async def main():
    """Función principal que inicia y gestiona el ciclo de vida del bot."""
    await bot.start(BOT_TOKEN) 

if __name__ == "__main__":
    
    # SOLUCIÓN ESPECÍFICA PARA WINDOWS: Cambia la política del bucle de eventos para manejar Ctrl+C
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        # Ejecuta la función principal
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Bot detenido por el usuario (Ctrl+C).")
        
    except discord.errors.LoginFailure:
        print("🛑 ERROR CRÍTICO: Token de Discord incorrecto. Por favor, genera un nuevo token en el Portal de Desarrolladores y reemplázalo en BOT_TOKEN.")

    except RuntimeError as e:
        # Captura y suprime el error al cerrar el bucle de eventos, que era tu problema inicial.
        if "Event loop is closed" in str(e) or "Event loop is running" in str(e):
             print("Bot detenido. RuntimeError (Event loop closed/running) suprimido.")
        else:
             raise

