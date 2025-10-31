import random
import string
from datetime import datetime

from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'trainer' or 'member'
    trainer_code = db.Column(db.String(6), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔹 Link each member to a trainer
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # 🔹 Self-referential relationship
    trainer = db.relationship(
        'User',
        remote_side=[id],
        backref=db.backref('members', lazy='dynamic')
    )

    # 🔹 Relationships
    progress = db.relationship("Progress", backref="user", cascade="all, delete-orphan")
    food_logs = db.relationship("UserFoodLog", backref="user", lazy=True)

    def generate_trainer_code(self):
        if self.role == 'trainer' and not self.trainer_code:
            characters = string.ascii_uppercase + string.digits
            self.trainer_code = ''.join(random.choices(characters, k=6))
            
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Float)
    protein_g = db.Column(db.Float)
    carbs_g = db.Column(db.Float)
    fats_g = db.Column(db.Float)
    source_id = db.Column(db.String(100))
    serving_size = db.Column(db.Float)
    serving_unit = db.Column(db.String(50))
    grams_per_unit = db.Column(db.Float)


UNIT_TO_GRAMS = {
    "g": 1,
    "kg": 1000,
    "oz": 28.35,
    "lb": 453.592,
    "tsp": 4.2,   # approximate
    "tbsp": 14.3,
    "cup": 240,
}

def _macro_basis(food):
    """Return macro values and a normalized serving size for the food."""
    base_protein = food.protein_g or 0
    base_carbs = food.carbs_g or 0
    base_fats = food.fats_g or 0
    base_calories = food.calories or 0

    serving_grams = food.serving_size or 100
    if not serving_grams:
        serving_grams = 100

    macros_total = base_protein + base_carbs + base_fats
    if serving_grams and macros_total:
        # USDA nutrients are stored per 100g. Some legacy foods report a
        # ``serving_size`` of 1 even though the macros clearly represent a
        # 100 gram basis (e.g. protein + carbs + fats greatly exceeds the
        # stated gram weight). Normalize those entries back to 100g so the
        # scaling factor remains correct.
        if macros_total > serving_grams * 1.5:
            serving_grams = 100

    return base_protein, base_carbs, base_fats, base_calories, serving_grams


class UserFoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default="g")  # <--- add this column
    log_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    food = db.relationship("Food")

    def _quantity_in_grams(self):
        """Return the stored quantity converted to grams."""
        quantity = self.quantity or 0
        unit = (self.unit or "g").lower()

        if unit == "g":
            return quantity

        measure = FoodMeasure.query.filter_by(food_id=self.food_id, measure_name=unit).first()
        if measure:
            return quantity * measure.grams

        grams_per_unit = UNIT_TO_GRAMS.get(unit)
        if grams_per_unit:
            return quantity * grams_per_unit

        return quantity

    @property
    def scaled(self):
        quantity_in_grams = self._quantity_in_grams()

        (
            base_protein,
            base_carbs,
            base_fats,
            base_calories,
            serving_grams,
        ) = _macro_basis(self.food)

        factor = quantity_in_grams / serving_grams if serving_grams else 0

        macro_calories = (base_protein * 4) + (base_carbs * 4) + (base_fats * 9)
        calories = base_calories

        if macro_calories:
            if not base_calories:
                calories = macro_calories
            else:
                ratio = base_calories / macro_calories if macro_calories else 0
                if ratio > 2 or ratio < 0.5:
                    calories = macro_calories

        return {
            "calories": round(calories * factor, 1),
            "protein": round(base_protein * factor, 1),
            "carbs": round(base_carbs * factor, 1),
            "fats": round(base_fats * factor, 1)
        }

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

class FoodMeasure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    measure_name = db.Column(db.String(50))  # "cup", "tbsp", "tsp", "slice"
    grams = db.Column(db.Float)              # how many grams that measure is

    food = db.relationship("Food", backref="measures")
