def start(bot, update):
    message = (
        "Hola, soy Cuervot!\n"
        "Sé hacer un par de cosas:\n\n"

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
    )
    update.message.reply_text(message, parse_mode='markdown')
