from flask import Blueprint, request, jsonify
from models import db, Pet, Milestone

bp = Blueprint('main', __name__)

@bp.route('/pets', methods=['POST'])
def create_pet():
    data = request.json
    new_pet = Pet(name=data['name'], breed=data['breed'], age=data['age'], adoption_date=data['adoption_date'])
    db.session.add(new_pet)
    db.session.commit()
    return jsonify({"id": new_pet.id}), 201

@bp.route('/pets/<int:pet_id>/milestones', methods=['POST'])
def add_milestone(pet_id):
    data = request.json
    new_milestone = Milestone(description=data['description'], date=data['date'], pet_id=pet_id)
    db.session.add(new_milestone)
    db.session.commit()
    return jsonify({"id": new_milestone.id}), 201

@bp.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([{ 'id': pet.id, 'name': pet.name, 'breed': pet.breed, 'age': pet.age, 'adoption_date': pet.adoption_date.strftime('%Y-%m-%d') } for pet in pets])
