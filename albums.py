import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import datetime
from bottle import HTTPError

DB_PATH = "sqlite:///albums.sqlite3"
Base = declarative_base()

class Album(Base):
    """
    Описывает структуру таблицы album для хранения записей музыкальной библиотеки
    """
    __tablename__ = "album"
    id = sa.Column(sa.INTEGER, primary_key=True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)

def connect_db():
    """
    Устанавливает соединение с базой данных, создаёт таблицы, если их еще нет и возвращает объект сессии 
    """
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

def find(artist):
    """
    Находит все записи в таблице album базы данных, у которых поле .artist соответствует заданному артисту
    """
    session = connect_db()
    albums = session.query(Album).filter(sa.func.lower(Album.artist) == artist.lower()).all()
    return albums

def find_saved(album):
    """
    Находит первую запись в таблице album, у которой поле .album соответствует искомому
    """
    session = connect_db()
    alb = session.query(Album).filter(sa.func.lower(Album.album) == album.lower()).first()
    return alb 

def valid_str(s): 
    """
    Проверяет строку на None, пустоту и наличие непечатаемых символов. Удаляет из строки
    ведущие, завершающие и лишние пробельные символы между словами. Делает первые буквы
    слов заглавными, остальные переводит в нижний регистр. При успешной проверке возвращает
    модифицированную строку, в противном случае - значение None 
    """ 
    if s is None:
        res = None
    else:
        s = s.strip().title()
        res = s
        s1 = s.split()
        for i in range(len(s1)):
            if s1[i] == "" or not (s1[i].isprintable() and s1[i] != ""):
                res = None
                break
            else:
                res = " ".join(s1)
    return res

def check_data(album_data):
    """
    Производит валидацию POST-запроса. При наличии ошибок генерирует соответствующие сообщения,
    при успешной проверке создаёт новую запись в базе данных и возвращает сообщение об успехе.
    """        
    result = "Данные успешно внесены в базу!"
    if not album_data["artist"]:
        message = f"Необходимо заполнить поле 'Артист' (не используйте спецсимволы). Попробуйте ещё раз!"
        result = HTTPError(400, message)
    elif not album_data["album"]:
        message = f"Необходимо заполнить поле 'Название альбома' (не используйте спецсимволы). Попробуйте ещё раз!"
        result = HTTPError(400, message)  
    elif not album_data["genre"]:
        message = f"Необходимо заполнить поле 'Жанр альбома' (не используйте спецсимволы). Попробуйте ещё раз!"
        result = HTTPError(400, message) 
    else:
        album_name = find_saved(album_data["album"])
        if album_name:
            message = f"Такой альбом ({album_name.album}) уже есть в базе. Попробуйте ещё раз!"
            result = HTTPError(400, message)
        else: 
            first_year = 1940 
            now_year = datetime.datetime.now().year
            try:
                album_year = int(album_data["year"])
            except ValueError as err:
                message = f"Необходимо указать год выхода альбома 4-х-значным числом в диапазоне от {first_year} до {now_year}. Попробуйте ещё раз!"
                result = f"Сервер вернул сообщение об ошибке: {str(err)}.\n{message}"
            except TypeError as err:
                message = f"Вы не указали год издания альбома."
                result = f"Сервер вернул сообщение об ошибке: {str(err)}.\n{message}"
            else:
                if not (first_year <= album_year <= now_year):
                    message = f"Год выхода альбома не может быть менее {first_year} и более {now_year}! Попробуйте уточнить данные."
                    result = HTTPError(400, message)
                else:                
                    create_album(album_data) 
            finally:
                pass                      
    return result           

def create_album(album_data):
    """
    Записывает информацию о новом альбоме в базу данных
    """    
    artist = album_data["artist"]
    genre = album_data["genre"]
    album = album_data["album"]
    year = album_data["year"]        
    # создаём новую запись
    new_album = Album(
        artist = artist,
        genre = genre,
        album = album,
        year = year
    )
    session = connect_db()    
    # добавляем новый альбом в сессию
    session.add(new_album)
    # сохраняем все изменения, накопленные в сессии
    session.commit()
    print("Данные успешно сохранены!")
    # возвращаем новую запись
    return new_album