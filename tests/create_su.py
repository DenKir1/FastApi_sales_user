# ===!!cli for superuser make

# ===!!fixture for headers testing

# # Arrange
# @pytest.fixture
# def fruit_bowl():
#     return [Fruit("apple"), Fruit("banana")]
#
#
# def test_fruit_salad(fruit_bowl):
#     # Act
#     fruit_salad = FruitSalad(*fruit_bowl)
#
#     # Assert
#     assert all(fruit.cubed for fruit in fruit_salad.fruit)

# ===  scr directory

# === == Pydantic model response (in class ModelPydantic !!!model_config=ConfigDict(from_attributes=True))

# from typing import List
#
# from pydantic import BaseModel, ConfigDict
#
#
# class PetCls:
#     def __init__(self, *, name: str, species: str):
#         self.name = name
#         self.species = species
#
#
# class PersonCls:
#     def __init__(self, *, name: str, age: float = None, pets: List[PetCls]):
#         self.name = name
#         self.age = age
#         self.pets = pets
#
#
# class Pet(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#
#     name: str
#     species: str
#
#
# class Person(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#
#     name: str
#     age: float = None
#     pets: List[Pet]
#
#
# bones = PetCls(name='Bones', species='dog')
# orion = PetCls(name='Orion', species='cat')
# anna = PersonCls(name='Anna', age=20, pets=[bones, orion])
# anna_model = Person.model_validate(anna)
# print(anna_model)
# """
# name='Anna' age=20.0 pets=[Pet(name='Bones', species='dog'), Pet(name='Orion', species='cat')]
# """

#  ===input params  !!!(rest architecture)

#  ===class Manager - get_user_list....

#  ===Readme update more screenshots add--


