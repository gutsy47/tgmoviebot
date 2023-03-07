import os
import gspread

from movieparser import FilmRu


class Service:
    def __init__(self):
        credentials = {
            "type": "service_account",
            "project_id": os.environ['GOOGLE_PROJECT_ID'],
            "private_key_id": os.environ["GOOGLE_PRIVATE_KEY_ID"],
            "private_key": os.environ["GOOGLE_PRIVATE_KEY"].replace('\\n', '\n'),
            "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ['GOOGLE_CLIENT_X509_CERT_URL']
        }
        account = gspread.service_account_from_dict(credentials)
        self.__spreadsheet = account.open("Bot data")
        self.__movies = []

    def get_post_template(self):
        worksheet = self.__spreadsheet.worksheet(title="Шаблон поста")
        return worksheet.cell(1, 1).value.replace('\\n', '\n')

    def update_post_template(self, template: str):
        worksheet = self.__spreadsheet.worksheet(title="Шаблон поста")
        worksheet.update_cell(1, 1, template)

    def __get_movies_db(self):
        worksheet = self.__spreadsheet.worksheet(title="БД Фильмов")
        values = worksheet.get_all_values()[1:]
        self.__movies = []
        for row in values:
            if not row[0]:
                break

            score = float(row[4].replace(',', '.'))
            if score >= 7:
                score = "🟢 " + str(score)
            elif score >= 5:
                score = "🟠 " + str(score)
            else:
                score = "🔴 " + str(score)

            self.__movies.append({
                "name": row[0],
                "isPosted": True if row[1] == "TRUE" else False,
                "year": row[2],
                "time": row[3],
                "score": score,
                "genres": [('#' + genre) for genre in row[5].replace(' ', '').split(',')],
                "description": row[6]
            })

    def get_post_amount(self, is_posted: bool = False):
        self.__get_movies_db()
        amount = 0
        for movie in self.__movies:
            if movie['isPosted'] == is_posted:
                amount += 1
        return amount

    def get_post_message(self, index: int = 0):
        template = self.get_post_template()
        i = 0
        post = None
        for movie in self.__movies:
            if movie["isPosted"]:
                continue

            if i == index:
                post = template \
                    .replace("name", movie["name"]) \
                    .replace("year", movie["year"]) \
                    .replace("time", movie["time"]) \
                    .replace("score", movie["score"]) \
                    .replace("genres", ", ".join(movie["genres"])) \
                    .replace("description", movie["description"])

            i += 1

        return post

    def set_movie_status_true(self, movie_index: int = 0):
        row = 1  # Row in table
        index = 0  # Index in not posted movies
        for movie in self.__movies:
            row += 1
            if movie["isPosted"]:
                continue
            if movie_index == index:
                worksheet = self.__spreadsheet.worksheet(title="БД Фильмов")
                worksheet.update_cell(row, 2, True)
                break
            index += 1
        else:
            return "No such movie"
        self.__get_movies_db()
        return movie["name"]
