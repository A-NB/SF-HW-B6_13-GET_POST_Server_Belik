from bottle import route
from bottle import run
from bottle import HTTPError
from bottle import request

import albums

# sqlite> .schema -- Структура таблиц в базе данных albums.sqlite3
# CREATE TABLE album ("id" integer primary key autoincrement, "year" integer, "artist" text,"genre" text,"album" text);
# CREATE TABLE sqlite_sequence(name,seq);

# Пример POST-запроса:

# http -f POST http://localhost:8080/albums artist="New Artist" genre="Rock" album="Super" year="1994"

@route("/albums/<artist>")
def find_albums(artist):
    artist = albums.valid_str(artist)
    albums_list = albums.find(artist)
    if not albums_list:
        message = f"Альбомов {artist} не найдено"
        result = HTTPError(404, message)
    else:
        album_count = len(albums_list)
        album_names = [album.album for album in albums_list]
        result = f"<ol>Количество найденных альбомов исполнителя {artist}: {album_count}<br>Список альбомов {artist}:<li>"
        result += "<li>".join(album_names)
        result += "</ol>"
    return result  

@route("/albums", method="POST")
def new_album():
    album_data = {
        "artist": albums.valid_str(request.forms.get("artist")),
        "genre": albums.valid_str(request.forms.get("genre")),
        "album": albums.valid_str(request.forms.get("album")),
        "year": albums.valid_str(request.forms.get("year"))
    }
    return albums.check_data(album_data)

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)