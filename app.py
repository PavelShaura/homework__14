import json
import sqlite3
from flask import Flask, jsonify


def main():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['DEBUG'] = True

    def get_movie(query):
        con = sqlite3.connect("netflix.db")
        cur = con.cursor()
        cur.execute(query)
        data = cur.fetchall()
        con.close()
        return data

    @app.route('/movie/<title>')
    def search_by_title(title):
        query = f"""
                 SELECT title, country, release_year, listed_in AS generate, description
                 FROM netflix
                 WHERE title = '{title}'
                 ORDER BY release_year DESC
                 LIMIT 1
                 """
        response = get_movie(query)[0]
        response_json = {
            'title': response[0],
            'country': response[1],
            'release_year': response[2],
            'generate': response[3],
            'description': response[4],
        }
        return jsonify(response_json)

    @app.route('/movie/<int:start>/to/<int:end>')
    def search_by_year(start, end):
        query = f"""
                SELECT title, release_year
                FROM netflix
                WHERE release_year BETWEEN {start} AND {end}
                ORDER BY release_year
                LIMIT 100
                """
        response = get_movie(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'release_year': film[1],
            })
        return jsonify(response_json)

    @app.route('/rating/<group>')
    def search_by_rating(group):
        levels = {
            'children': ['G'],
            'family': ['G', 'PG', 'PG-13'],
            'adult': ['R', 'NC -17'],
        }

        if group in levels:
            level = '\", \"'.join(levels[group])
            level = f'\"{level}\"'
        else:
            return jsonify([])

        query = f"""
                SELECT title, rating, description
                FROM netflix
                WHERE rating IN {level}
                """
        print(query)
        response = get_movie(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'rating': film[1],
                'description': film[2],
            })
        return jsonify(response_json)

    @app.route('/genre/<genre>')
    def search_by_genre(genre):
        query = f"""
                    SELECT title, description, listed_in
                    FROM netflix
                    WHERE listed_in LIKE '%{genre}%'
                    ORDER BY release_year DESC
                    LIMIT 10
                    """
        response = get_movie(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1],
            })
        return jsonify(response_json)

    def get_actors(name_1, name_2):

        query = f"""
                SELECT "cast"
                FROM netflix
                WHERE "cast" LIKE '%{name_1}%'
                AND "cast" LIKE '%{name_2}%'
                """
        response = get_movie(query)
        actors = []
        for cast in response:
            actors.extend(cast[0].split(', '))
        result = []
        for q in actors:
            if q not in [name_1, name_2]:
                if actors.count(q) > 2:
                    result.append(q)
        result = set(result)
        return result

    def get_films(type_film, release_year, genre):

        query = f"""
                SELECT title, description
                FROM netflix
                WHERE "type" = '{type_film}'
                AND release_year LIKE '{release_year}'
                AND listed_in LIKE '{genre}'
                """

        response = get_movie(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1],
            })

        with open('my.json', 'w', encoding='utf-8') as file:
            json.dump(response_json, file, indent=4, ensure_ascii=False)

        return response_json

    print(get_actors(name_1='Rose McIver', name_2='Ben Lamb'))
    print(get_films(type_film='Movie', release_year='2016', genre='Dramas'))

    app.run()


if __name__ == '__main__':
    main()
