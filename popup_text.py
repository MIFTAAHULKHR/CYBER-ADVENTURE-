from messages import *

def show_opening_popup(display_surface):
    
    opening_text = [
        "Di dunia maya yang penuh dengan data dan sistem yang saling terhubung.",
        "Sebuah ancaman besar mulai muncul.",
        "Virus-virus yang sangat canggih telah menyusupi sistem vital dan berbahaya.",
        "Jaringan yang dulu aman kini hancur dan berada di ambang kehancuran.",
        "Dunia ini butuh seorang pahlawan untuk menghadapinya."
    ]

    show_text = Message(opening_text, display_surface)
    # , -850, -150)
    show_text.run()

def show_key(display_surface):
    text_poison2 = [
        "Kamu menemukan ramuan yang cukup ampuh.",
        "Keluargamu sembuh untuk sementara waktu, namun...",
        "kamu harus terus mencari ramuan lain untuk penyembuhan yang lebih permanen."
    ]
    show_text = Message(text_poison2, display_surface)
    show_text.run()

def show_death(display_surface):
    text_death = [
        "Dalam pencarian putus asa untuk obat penyembuh...",
        "pemuda berkelana menemui ajal di dalam hutan gelap...",
        "Harapan penyelamatan bagi keluarganya pupus bersama dengan kepergiannya!!!"
    ]
    show_text = Message(text_death, display_surface)
    show_text.run()    