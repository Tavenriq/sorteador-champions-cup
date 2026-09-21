from PIL import Image

img = Image.open("SortApp/static/logoCCC.png")

img = img.resize((32, 32), Image.Resampling.LANCZOS)

img.save("SortApp/static/favicon.ico")

print("Favicon gerado com sucesso!")
