from dubina import WebPage

page = WebPage(host="0.0.0.0", port=7000, title_message="Дубина", connect_to_port=50055)
page.start()
