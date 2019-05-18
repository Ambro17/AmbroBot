from updater import elbot


@elbot.route(command='start')
def start(bot, update):
    message = (
        "🇦🇷 Hi, i'm Cuervot! \n"
        "These are my skills:\n\n"
        "/dolar - Cotización del dólar\n"
        "/rofex - Cotizacion dólar futuro\n"
        "/subte - Estado de subtes CABA\n"
        "/pelicula - Buscar detalle de pelicula\n"
        "/hoypido - Ver menú de hoypido\n"
        "/serie - Descargar capitulos de series por torrent\n"
        "/yts - Ver ultimas peliculas de yts\n"
        "/feriados - Ver próximos feriados de Argentina\n"
        "/snippets - Snippets de codigo/troubleshooting/cualquier cosa\n"
        "/partido - Próximo partido de San Lorenzo\n"
        "/posiciones - Tabla de posiciones Argenntina\n"
        "/cartelera - Peliculas más populares en cartelera\n"
        "/aproximar - Calcular la solución del sistema de ecuaciones lineales\n\n"
        "If you find any bug or suggestion, you can send it through /feedback\n"
        "I'm also open source so you can see how i work with /code"
    )
    update.message.reply_text(message, parse_mode='markdown', disable_web_page_preview=True)
