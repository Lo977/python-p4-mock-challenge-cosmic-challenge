#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)
db.init_app(app)


@app.route('/')
def home():
    return 'Welcome to the Space Missions API!'


class ScientistResource(Resource):
    def get(self, scientist_id=None):
        if scientist_id is not None:
            scientist = Scientist.query.get(scientist_id)
            if scientist:
                return scientist.to_dict(), 200
            return {"error": "Scientist not found"}, 404
        scientists = Scientist.query.all()
        return [scientist.to_dict(rules=('-missions',)) for scientist in scientists], 200

    def post(self):
        try:
            data = request.get_json()
            name = data['name']
            field_of_study = data['field_of_study']
            if not name or not field_of_study:
                raise ValueError

            new_scientist = Scientist(
                name=name,
                field_of_study=field_of_study
            )
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except Exception:
            return {
                "errors": ["validation errors"]
            }, 422

    def patch(self, scientist_id=None):
        scientist = Scientist.query.get(scientist_id)
        if not scientist:
            return {
                "error": "Scientist not found"
            }, 404
        try:
            data = request.get_json()
            scientist.name = data['name']
            scientist.field_of_study = data['field_of_study']
            db.session.commit()
            return scientist.to_dict(), 202
        except Exception:
            return {
                "errors": ["validation errors"]
            }, 404

    def delete(self, scientist_id=None):
        scientist = Scientist.query.get(scientist_id)
        if not scientist:
            return {
                "error": "Scientist not found"
            }, 404
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204


class PlanetsResource(Resource):
    def get(self):
        return [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()], 200


class MissionsResource(Resource):
    def post(self):
        data = request.get_json()
        name = data['name']
        scientist_id = data['scientist_id']
        planet_id = data['planet_id']
        if not name or not scientist_id or not planet_id:
            raise ValueError
        try:
            new_mission = Mission(
                name=name,
                scientist_id=scientist_id,
                planet_id=planet_id
            )
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except Exception:
            return {'error': ["validation errors"]}, 404


api.add_resource(ScientistResource, '/scientists',
                 '/scientists/<int:scientist_id>')
api.add_resource(PlanetsResource, "/planets")
api.add_resource(MissionsResource, "/missions")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
