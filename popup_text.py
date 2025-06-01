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
        "Dengan ketangkasan dan kecerdasanmu, semua virus berhasil dikalahkan.",
        "Sistem vital kini pulih, jaringan kembali aman dan stabil.",
        "Dunia maya yang tadinya gelap mulai bersinar kembali.",
        "Kau bukan hanya menyelamatkan data, tapi masa depan seluruh jaringan.",
        "Kau bukan sekadar pahlawan...  tugasmu telah selesai. Untuk sekarang."
    ]
    show_text = Message(text_poison2, display_surface)
    show_text.run()
    return "victory"

def show_death(display_surface):
    text_death = [
        "Virus terlalu kuat dan pertahanan sistem telah runtuh.",
        "Data penting hilang, dan jaringan hancur tak bisa diperbaiki.",
        "Upaya kerasmu belum cukup untuk menghentikan kehancuran ini.",
        "Dunia maya terbenam dalam kekacauan dan kegelapan.",
        "Namun harapan belum sepenuhnya hilang... Akan ada kesempatan berikutnya."
    ]
    show_text = Message(text_death, display_surface)
    show_text.run()
    return 'gameover'   