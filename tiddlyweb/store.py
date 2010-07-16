"""
Put and Get TiddlyWeb things to and from some store.
"""

class StoreError(IOError):
    """
    Base Exception for Store Exceptions.
    """
    def __str__(self):
        # self.args may or may not be a string, and when that
        # is the case is proving rather difficult to tell between
        # minor and micro versions of Python. woot!
        # So here we do some extra work.
        message = []
        for arg in self.args:
            if isinstance(arg, basestring):
                message.append(arg)
        return ' '.join(message)


class StoreMethodNotImplemented(StoreError):
    """
    A StorageInterface does not implement this method.
    """
    pass


class NoBagError(StoreError):
    """
    No Bag was found.
    """
    pass


class NoRecipeError(StoreError):
    """
    No Recipe was found.
    """
    pass


class NoTiddlerError(StoreError):
    """
    No Tiddler was found.
    """
    pass


class NoUserError(StoreError):
    """
    No User was found.
    """
    pass


class StoreLockError(StoreError):
    """
    This process was unable to get a lock on the store.
    """
    pass


class StoreEncodingError(StoreError):
    """
    Something about an entity made it impossible to be
    encoded to the form require by the store.
    """
    pass


class Store(object):
    """
    Provide a facade around implementations of StorageInterface
    to handle the storage and retrieval of TiddlyWeb entities
    to and from persistent storage.
    """

    def __init__(self, engine, config=None, environ=None):
        if config == None:
            config = {}
        self.engine = engine
        self.environ = environ
        self.storage = None
        self.config = config
        self._import()

    def _import(self):
        """
        Import the required StorageInterface.
        """
        try:
            imported_module = __import__('tiddlyweb.stores.%s' % self.engine,
                    {}, {}, ['Store'])
        except ImportError, err:
            err1 = err
            try:
                imported_module = __import__(self.engine, {}, {}, ['Store'])
            except ImportError, err:
                raise ImportError("couldn't load store for %s: %s, %s" % (self.engine, err, err1))
        self.storage = imported_module.Store(self.config, self.environ)

    def delete(self, thing):
        """
        Delete a known object.
        """
        func = self._figure_function('delete', thing)
        return func(thing)

    def get(self, thing):
        """
        Get a thing, recipe, bag or tiddler
        """
        func = self._figure_function('get', thing)
        thing = func(thing)
        thing.store = self
        return thing

    def put(self, thing):
        """
        Put a thing, recipe, bag or tiddler.

        Should there be handling here for things of
        wrong type?
        """
        func = self._figure_function('put', thing)
        return func(thing)

    def _figure_function(self, activity, storable):
        """
        Determine which function on the StorageInterface
        we should use to store or retrieve storable.
        """
        lower_class = storable.__class__.__name__.lower()
        try:
            func = getattr(self.storage, '%s_%s' % (lower_class, activity))
        except AttributeError, exc:
            raise AttributeError('unable to figure function for %s: %s' % (lower_class, exc))
        return func

    def list_bags(self):
        """
        List all the available bags in the system.
        """
        list_func = getattr(self.storage, 'list_bags')
        return list_func()

    def list_bag_tiddlers(self, bag):
        """
        List all the tiddlers in the bag.
        """
        list_func = getattr(self.storage, 'list_bag_tiddlers')
        return list_func(bag)

    def list_recipes(self):
        """
        List all the available recipes in the system.
        """
        list_func = getattr(self.storage, 'list_recipes')
        return list_func()

    def list_tiddler_revisions(self, tiddler):
        """
        List the revision ids of the revisions of the indicated tiddler.
        """
        list_func = getattr(self.storage, 'list_tiddler_revisions')
        return list_func(tiddler)

    def list_users(self):
        """
        List all the available users in the system.
        """
        list_func = getattr(self.storage, 'list_users')
        return list_func()

    def search(self, search_query):
        """
        Search in the store, using a search algorithm
        specific to the StorageInterface implementation.
        """
        list_func = getattr(self.storage, 'search')
        return list_func(search_query)
