import data.db_session as db_session
from data.recipes import Recipe
from data.users import User
import json
from random import choice


class Command:
    def __init__(self, my_bot, name, description):
        self.my_bot = my_bot
        self.name = name
        self.description = description

    def execute(self, *args):
        pass

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description


class HowToPrepare(Command):
    """
    This command accepts the name of the dish from the user and returns the ingredients and cooking method
    """

    def __init__(self, my_bot, name, description):
        self.flag = 0
        super().__init__(my_bot, name, description)

    def execute(self, *args):
        db_sess = db_session.create_session()
        meal = args[0]
        dishes = [el.name for el in db_sess.query(Recipe).all()]
        similar_dishes = [dish for dish in dishes if dish.startswith(meal)]
        for dish in dishes:
            if dish == meal:
                my_query = db_sess.query(Recipe).filter(Recipe.name == meal)
                for elem in my_query:
                    splitted_elem_ingridients = elem.ingridients.split(" ,")
                    splitted_cooking_method = elem.cooking_method.split(" ,")
                    return 'Ингридиенты:' + "\n" + "\n".join(splitted_elem_ingridients) + "\n" + 'Способ\
                     приготовления' + "\n" + "\n".join(splitted_cooking_method)
            elif dish != meal:
                if len(similar_dishes) > 0:
                    self.flag = 1
                    return "Какое именно из этих блюд вы хотите приготовить?" + "\n" + "\n".join(similar_dishes)
                else:
                    return 'На данный момент такого рецепта нет в базе данных. Возможно, он появится в будущем, следите\
                     за обновлениями'


class WhatToCookFrom(Command):
    """
    This command gets a list of ingredients from the user and returns the names of
    dishes that can be prepared from them
    """

    def __init__(self, my_bot, name, description):
        super().__init__(my_bot, name, description)

    def execute(self, *args):
        result = set()
        db_sess = db_session.create_session()
        user_ings = args[0].split('/')
        print(args)
        all_recipe_info = db_sess.query(Recipe).all()
        for elem in all_recipe_info:
            recipe_ings = elem.ingridients
            for ing in user_ings:
                if ing in recipe_ings:
                    result.add(elem.name)
        if result:
            return "Вы можете приготовить:" + "\n" + "\n".join(list(result))
        else:
            return 'Вы ничего не можете с этими ингредиентами приготовить'


class RandomMeal(Command):
    def __init__(self, my_bot, name, description):
        super().__init__(my_bot, name, description)

    def execute(self):
        db_sess = db_session.create_session()
        elem = choice(db_sess.query(Recipe).all())
        if elem != None:
            return f'Я выбрал случайное блюдо: {elem.name}' + '\n' + 'Ингридиенты:' + "\n" + "\n".join(
                elem.ingridients.split(' ,')) + "\n" + 'Способ приготовления:' + "\n" \
                   + "\n".join(elem.cooking_method.split(' ,') + "\n".join(elem.nutrition_facts.split("/")))
        else:
            return self.execute()


class AddMeal(Command):
    """
    This command accepts from the user the name of the dish, the list of ingredients, the method of preparation and adds
    a new recipe to the database
    """

    def __init__(self, my_bot, name, description):
        super().__init__(my_bot, name, description)
        self.execute_all()

    def create_recipe(self, name, ingridients, cooking_method, nutrition_facts):
        new_recipe = Recipe()
        new_recipe.name = name
        new_recipe.ingridients = ingridients
        new_recipe.cooking_method = cooking_method
        new_recipe.nutrition_facts = nutrition_facts
        return new_recipe

    def create_user(self, user_id, char):
        new_user = User()
        new_user.user_id = user_id
        new_user.have_admin = char
        return new_user

    def execute_all(self):
        db_sess = db_session.create_session()
        with open('data/meals.json', 'r', encoding='UTF-8') as meals:
            data = json.load(meals)
        for key, value in data.items():
            recipe = db_sess.query(Recipe).filter(Recipe.name == key).first()
            if not recipe:
                new_recipe = self.create_recipe(key, " ,".join(value["ingridients"]),
                                                " ,".join(value["cooking_method"]),
                                                "/".join(value["nutrition_facts"]))
                db_sess.add(new_recipe)
                db_sess.commit()

    def execute(self, user_id, *args):
        db_sess = db_session.create_session()
        meal_name = args[0]
        meal_ingridients = args[1]
        meal_cooking_method = args[2]
        meal_nutrition_facts = args[3]
        user = db_sess.query(User).filter(User.user_id == user_id).first()
        if user:
            recipe = db_sess.query(Recipe).filter(Recipe.name == meal_name).first()
            if not recipe:
                new_recipe = self.create_recipe(meal_name, meal_ingridients, meal_cooking_method, meal_nutrition_facts)
                db_sess.add(new_recipe)
                db_sess.commit()
                return "рецепт успешно добавлен"
            else:
                return "такой рецепт уже есть"
        else:
            return "Вы не являетесь администратором"

    def set_admin(self, user_id, password):
        check_password = 'Сарсапарилла'
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.user_id == user_id).first()
        if user:
            return "Вы уже администратор!"
        elif password == check_password:
            new_admin = self.create_user(user_id, 1)
            db_sess.add(new_admin)
            db_sess.commit()
            return "Теперь вы админ!"
        else:
            return "Неправильный пароль"


class Help(Command):
    def __init__(self, my_bot, name, description):
        super().__init__(my_bot, name, description)

    def execute(self):
        return '''
        Вот что я умею:
        add_meal; <ингредиент1 ,ингредиент2 ,...>; <действие1 ,действие2 ,...> - добавление блюда в базу данных
        how_to_prepare; <название блюда> - получение рецепта блюда
        what_to_cook_from; <ингредиент1/ингредиент2...> - получение названия блюда, которое можно сделать из \
                                                                 введенных ингридиентов
        random_meal - получение названия случайного блюда из базы данных
        add_meal; set_admin; <Пароль модератора> - сделать пользователя модератором
        '''

