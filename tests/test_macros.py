from app import db
from app.models import Food, FoodMeasure, User, UserFoodLog
from app.routes.member import scale_nutrients


def _seed_food():
    food = Food(
        name="Sample Food",
        calories=200,
        protein_g=20,
        carbs_g=10,
        fats_g=5,
        serving_size=100,
        serving_unit="g",
    )
    db.session.add(food)
    db.session.commit()
    return food


def test_scaled_macros_from_gram_quantity(app_context):
    food = _seed_food()
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password_hash="hash",
        role="member",
    )
    db.session.add(user)
    db.session.commit()

    log = UserFoodLog(user_id=user.id, food_id=food.id, quantity=150, unit="g")
    db.session.add(log)
    db.session.commit()

    assert log.scaled["calories"] == 300
    assert log.scaled["protein"] == 30
    assert log.scaled["carbs"] == 15
    assert log.scaled["fats"] == 7.5


def test_scaled_macros_with_measure_conversion(app_context):
    food = _seed_food()
    user = User(
        first_name="Test",
        last_name="User",
        email="test2@example.com",
        password_hash="hash",
        role="member",
    )
    db.session.add(user)
    db.session.commit()

    measure = FoodMeasure(food_id=food.id, measure_name="cup", grams=120)
    db.session.add(measure)
    db.session.commit()

    log = UserFoodLog(user_id=user.id, food_id=food.id, quantity=2, unit="cup")
    db.session.add(log)
    db.session.commit()

    # 2 cups -> 240 grams, factor = 240/100 = 2.4
    assert log.scaled["calories"] == 480
    assert log.scaled["protein"] == 48
    assert log.scaled["carbs"] == 24
    assert log.scaled["fats"] == 12


def test_scaled_calories_from_macros_when_energy_is_kj(app_context):
    food = Food(
        name="Cheddar Cheese",
        calories=1710,  # stored as kilojoules
        protein_g=25,
        carbs_g=1,
        fats_g=33,
        serving_size=100,
        serving_unit="g",
    )
    db.session.add(food)
    db.session.commit()

    user = User(
        first_name="Test",
        last_name="User",
        email="cheddar@example.com",
        password_hash="hash",
        role="member",
    )
    db.session.add(user)
    db.session.commit()

    log = UserFoodLog(user_id=user.id, food_id=food.id, quantity=100, unit="g")
    db.session.add(log)
    db.session.commit()

    assert log.scaled["calories"] == 401.0


def test_scale_nutrients_uses_macro_calories(app_context):
    food = Food(
        name="Cheddar Cheese",
        calories=1710,
        protein_g=25,
        carbs_g=1,
        fats_g=33,
        serving_size=100,
        serving_unit="g",
    )
    db.session.add(food)
    db.session.commit()

    scaled = scale_nutrients(food.id, 100, "g")

    assert scaled["calories"] == 401.0
    assert scaled["protein_g"] == 25.0
    assert scaled["carbs"] == 1.0
    assert scaled["fats"] == 33.0


def test_scale_nutrients_normalizes_min_serving_foods(app_context):
    food = Food(
        name="Cheddar Cheese",
        calories=1710,
        protein_g=25,
        carbs_g=1,
        fats_g=33,
        serving_size=1,
        serving_unit="g",
    )
    db.session.add(food)
    db.session.commit()

    scaled = scale_nutrients(food.id, 100, "g")

    assert scaled["calories"] == 401.0
    assert scaled["protein_g"] == 25.0
    assert scaled["carbs"] == 1.0
    assert scaled["fats"] == 33.0


def test_search_foods_uses_macro_calories(app_client):
    _, client = app_client

    food = Food(
        name="Cheddar Cheese",
        calories=1710,
        protein_g=25,
        carbs_g=1,
        fats_g=33,
        serving_size=100,
        serving_unit="g",
    )
    db.session.add(food)
    db.session.commit()

    response = client.get(
        "/member/search-foods",
        query_string={"q": "cheddar", "unit": "g", "quantity": "100"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["results"], "expected at least one search result"
    result = data["results"][0]

    assert result["calories"] == 401.0
    assert result["protein_g"] == 25.0
    assert result["carbs"] == 1.0
    assert result["fats"] == 33.0


def test_log_scaled_normalizes_min_serving_foods(app_context):
    food = Food(
        name="Cheddar Cheese",
        calories=1710,
        protein_g=25,
        carbs_g=1,
        fats_g=33,
        serving_size=1,
        serving_unit="g",
    )
    db.session.add(food)
    db.session.commit()

    user = User(
        first_name="Test",
        last_name="User",
        email="legacy@example.com",
        password_hash="hash",
        role="member",
    )
    db.session.add(user)
    db.session.commit()

    log = UserFoodLog(user_id=user.id, food_id=food.id, quantity=100, unit="g")
    db.session.add(log)
    db.session.commit()

    assert log.scaled["calories"] == 401.0
    assert log.scaled["protein"] == 25.0
    assert log.scaled["carbs"] == 1.0
    assert log.scaled["fats"] == 33.0
