"""
Simple functions for storing stuff as textfiles
on the filesystem.
"""

store_root = 'store'

from google.appengine.ext import db

from tiddlyweb.bag import Bag, Policy
from tiddlyweb.recipe import Recipe
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, NoUserError, StoreLockError
from tiddlyweb.stores import StorageInterface

class GDRecipe(db.Model):
    name = db.StringProperty(required=True)
    recipe = db.ListProperty(unicode)

class GDBag(db.Model):
    name = db.StringProperty(required=True)
    tiddlers = db.ListProperty(unicode)

class GDTiddler(db.Model):
    title = db.StringProperty(required=True)
    modifier = db.StringProperty()
    modified = db.StringProperty()
    created = db.StringProperty()
    tags = db.ListProperty(unicode)
    text = db.TextProperty()
    bag = db.StringProperty()

class Store(StorageInterface):

    def recipe_get(self, recipe):
        recipe_query = GDRecipe.gql('WHERE name = :1')
        recipe_query.bind(recipe.name)
        gdrecipe = recipe_query.get()
        
        recipe_list = []
        for line in gdrecipe.recipe:
            bag, filter = line.split('?')
            recipe_list.append([bag, filter])

        recipe.set_recipe(recipe_list)
        return recipe

    def recipe_put(self, recipe):
        gdrecipe = GDRecipe(key_name='key:%s' % recipe.name, name=recipe.name)
        recipe_list = []
        for bag, filter in recipe.get_recipe():
            line = '%s?%s' % (bag, filter)
            recipe_list.append(line)
        gdrecipe.recipe = recipe_list
        gdrecipe.put()

    def bag_get(self, bag):
        bag_query = GDBag.gql('WHERE name = :1')
        bag_tiddler_query = GDTiddler.gql('WHERE bag = :1')

        bag_query.bind(bag.name)
        gdbag = bag_query.get()

        bag_tiddler_query.bind(bag.name)
        
        for gdtiddler in bag_tiddler_query:
            tiddler = Tiddler(gdtiddler.title)
            bag.add_tiddler(tiddler)

# ignore policy for now, use the default

        return bag

    def bag_put(self, bag):
        gdbag = GDBag(key_name='key:%s' % bag.name, name=bag.name)
        gdbag.put()

    def tiddler_get(self, tiddler):
        tiddler_query = GDTiddler.gql('WHERE title = :1 and bag = :2')
        tiddler_query.bind(tiddler.title, tiddler.bag)
        gdtiddler = tiddler_query.get()

        # be explicit for now
        tiddler.modifier = gdtiddler.modifier
        tiddler.modified = gdtiddler.modified
        tiddler.created = gdtiddler.created
        tiddler.text = gdtiddler.text
        tiddler.tags = gdtiddler.tags

        return tiddler

    def tiddler_put(self, tiddler):
        gdtiddler = GDTiddler(key_name='key:%s:%s' % (tiddler.title, tiddler.bag), title=tiddler.title, bag=tiddler.bag)
        gdtiddler.modifier = tiddler.modifier
        gdtiddler.modified = tiddler.modified
        gdtiddler.created = tiddler.created
        gdtiddler.text = tiddler.text
        gdtiddler.tags = tiddler.tags
        gdtiddler.put()

    def user_get(self, user):
        pass

    def user_put(self, user):
        pass

    def list_recipes(self):
        q = GDRecipe.all()

        recipes = []
        try:
            for gdrecipe in q:
                recipe = Recipe(gdrecipe.name)
                recipe_list = []
                for line in gdrecipe.recipe:
                    bag, filter = line.split('?')
                    recipe_list.append([bag, filter])
                recipe.set_recipe(recipe_list)
                recipes.append(recipe)
        except TypeError:
            pass

        return recipes

    def list_bags(self):
        q = GDBag.all()

        try:
            return [Bag(bag.name) for bag in q]
        except TypeError:
            return []

    def list_tiddler_revisions(self, tiddler):
        return []
