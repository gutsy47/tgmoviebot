import requests
from bs4 import BeautifulSoup


class FilmRu:

    URL = "https://www.film.ru"

    def __init__(self, request: str):

        # Data from the search query
        self.query = self.get_query(request=request)
        self.link, self.name, self.poster = self.query.pop(0)

        # Data from the movie's page
        details = self.get_details()
        self.year = details["year"]
        self.time = details["time"]
        self.rating = details["rating"]
        self.genres = details["genres"]

    @staticmethod
    def get_query(request):
        """
        Returns all the found movies from the search query
        :return: {str movieName : str movieLink}
        """
        url = f"{FilmRu.URL}/search/result?text={request.lower().replace(' ', '+')}&type=movies&s=rel"
        # print(url)
        response = requests.get(url)
        soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')

        query = []
        for movie in soup.find("div", {"class": "rating", "id": "movies_list"}).find_all("a"):
            link = FilmRu.URL + movie.attrs["href"]
            name = movie.find("img").attrs["alt"]
            poster = movie.find("img").attrs["src"]
            query.append([link, name, poster])

        return query

    def set_next_movie(self):
        """Updates the link to the movie and it's details (if first one from query is not the right one"""
        self.link, self.name, self.poster = self.query.pop(0)

        # Update details
        details = self.get_details()
        self.year = details["year"]
        self.time = details["time"]
        self.rating = details["rating"]
        self.genres = details["genres"]

    def get_details(self):
        """Gets all the required data from the movie's link"""
        details = {}

        response = requests.get(self.link)
        soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')

        details["year"] = soup.find("a", {"itemprop": "dateCreated"}).text
        details["genres"] = [a.text for a in soup.find_all("a", {"itemprop": "genre"})]
        details["time"] = soup.find("strong", {"itemprop": "duration"}).attrs["content"][4:9]
        details["rating"] = soup.find("strong", {"id": "movie_rate"}).text.strip().split()[0]

        return details
