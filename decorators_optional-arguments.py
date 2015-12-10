def decorator(*conf_args, **conf_kwargs):
    """
    Decorator which may be called with or without configuration arguments, like so:
        1. @decorator, translated into
             -> decorator(func)(*args, **kwargs)
        2. @decorator(*conf_args, **conf_kwargs), translated into
             -> decorator(*conf_args, **conf_kwargs)(func)(*args, **kwargs)
    """
    print("""  decorator(*conf_args=%s, **conf_kwargs=%s""" % (conf_args, conf_kwargs))
    def decorator_(obj):
        """
        Logging decorator for API methods,
        Loging in and out params per method called.
        """
        print("""  decorator.decorator_(
            obj=%s""" % obj)

        nameunset = '__name__', 'unset'
        obj_name = getattr(obj, *nameunset)

        def wrapper(*args, **kwargs):
            print(chr(95)*90, """\n  decorator.decorator_.wrapper(
            *args=%s, **kwargs=%s""" % (args, kwargs))

            slice_start = (2, 0)[configured]
            slice_obj = slice(slice_start, slice_start+2)
            cfg = ("", "following", "NOT ", "any")[slice_obj] + (len(conf_args) > 0 and conf_args[0] is obj,)

            print("""  -- decorator was %sgiven %s configurations:
            1. conf_args[0] is obj -> %s,
            2. *conf_args=%%s, *conf_kwargs==%%s""" % cfg % (conf_args, conf_kwargs))

            # if decorator was configured...
            dec_config = conf_kwargs.get('dec_config', {})
            trojan = dec_config.get('alternative')
            alternative_name = dec_config.get('change_name')

            if trojan:
                # obj.__dict__['_trojan'] = trojan
                setattr(obj, '_trojan', trojan)
            elif alternative_name:
                obj.__name__ = alternative_name

            result = obj(*args, **kwargs)

            if trojan:
                print("""  decorator.decorator_.wrapper(
            decorator has modified underlying object. It's a mutation.""")
            return result
        return wrapper

    # router
    if (len(conf_args) == 1         # decorating a function, a class or a method
        and callable(*conf_args)    # must be top-level callable - @decorator() w/o args will be left out
        and not conf_kwargs):       # must not have anything else accompanying

        configured = False
        # called as @decorator -> decorator(func) with obj as the _only_ argument
        # manually enforce calling next layer of wrapping
        # stay identical after that when actual instantiation happens
        return decorator_(*conf_args)

    else:

        configured = True
        # @decorator(*conf_args, **conf_kwargs) -> decorator(*conf_args, **conf_kwargs)(func)
        # decorator was called with config arguments; return normal layer of wrapping
        # next call will provide the decorator_ with an obj.
        # It was manually enforced in the technique above.
        return decorator_


class xClass(object):
    """
    For magic methods the lookup is always done on the class.

    class MyClass(metaclass=MyMetaClass) gets translated into
    MyClass = MyMetaClass(name, bases, **kwargs) - it's a MyMetaClass instance.

    Configuring class creation achieved by sending keyword arguments to it's metaclass.
    > Take elements in _attrs and make them class attributes with value 0
    """
    _attrs = ['A', 'B']
    def __new__(cls, arg, kw_arg=None):
        """
        cls.__new__ is used to create instances of cls.
        It's a staticmethod with first argument => cls, where
        return value of __new__() will a new Instance (usually an instance of cls).

        Create a new _instance_ of the class by invoking the superclass’s __new__() method
        using super(current_class, cls).__new__(cls [, ...]), which is the same as super(cls, cls).__new__(cls)
        #>> <__main__.cls object at 0xMemAddr>, and then modify newly created class (instance of Meta) if needed.

        IMPORTANT: If __new__() DOES NOT RETURN AN_INSTANCE_OF_cls ->  __init__ WILL NOT BE INVOKED.
        (because, newly created object may not have an __init__ method defined)

        MAINLY, __new__ IS INTENDED TO ALLOW IMMUTABLE TYPE (INT, STR, TUPLE) SUBCLASSES TO CUSTOMIZE INSTANCE CREATION.
        It is also commonly overridden in metaclasses in order to customize class creation.

        When the class defines __new__, it will be looked up on the same object (the class),
        not on a upper level (in a metaclass or parent object) like all the rest of magic methods.
        This is important to understand, because both the class and the metaclass can define this method.
        """
        _fmt = """
            cls=%s,
            arg=%s, kw_arg=%s""" % (cls, arg, kw_arg)
        print('  xClass.__new__(%s)' % _fmt)

        #  super(), super(__class__, cls), ->  superclass is a wrapper around cls
        #  super().__new__(cls)  ->  <__main__.xClass object at 0xMemAddr>
        #  object.__new__(cls) ->  <__main__.xClass object at 0xMemAddr>
        #  super().__self_class__ == super().__thisclass__ == cls -> True  # wrapped object
        _super = super()  # -> <super: <class 'xClass'>, <xClass object>>
        print('  --- call to super() returns %s' % _super)

        trojan = getattr(cls, '_trojan', None)
        if trojan:
            obj = _super.__new__(type(trojan, (object,), {}))
            desc = 'directly, without __init__ invocation'
        else:
            obj = _super.__new__(cls) # needs to be a class not type
            desc = 'to __init__' # internally, isinstance(obj, cls) is performed before __init__...
        print('  --- dispatching %s %s' % (obj, desc))
        return obj  # ...and if __new__ returned not an instance of a cls, __init__ will be skipped

    def __init__(self, arg, kw_arg=None):
        """
        Received an instance created in __new__
        Remaining arguments *are the same* as were passed to __new__
        """
        _fmt = """
            self=%s,
            arg=%s, kw_arg=%s""" % (self, arg, kw_arg)
        print("""  xClass.__init__(%s)""" % _fmt)
        self.arg = arg
        self.kw_arg = kw_arg
        return super().__init__()

    def __str__(self):
        attrs = dict((k, getattr(self, k)) for k in dir(self) if not k.startswith(chr(95)*2))
        _args = self.__class__.__name__, getattr(self, 'arg', 'MISSING'), \
                getattr(self, 'kw_arg', 'MISSING'), attrs
        return """<an Instance of xClass, named %s:
            arg=%s, kw_arg=%s,
            **instance-attributes=%s>""" % _args


#### FLIGHT
########################
change_name = dict(change_name='Hello world!')
alternative = dict(alternative='AlternativeClass')

# no args, equal to
# @decorator
# ...
print('w returns %s' % decorator(xClass)('pos_arg'))

# empty args, equal to
# @decorator()
# ...
print('x returns %s' % decorator()(xClass)('pos_arg'))

# modifying class name, equal to
# @decorator(arg1, arg2)
# ...
print('y returns %s' % decorator('dec_posarg', dec_config=change_name)(xClass)('pos_arg', 'kw_arg'))

# returning alternative object, equal to
# @decorator(...)
# ...class Xclass...
print('z returns %s' % decorator('dec_posarg', dec_config=alternative)(xClass)('pos_arg', 'kw_arg'))


#   decorator(*conf_args=(<class '__main__.xClass'>,), **conf_kwargs={}
#   decorator.decorator_(
#             obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg',), **kwargs={}
#   -- decorator was NOT given any configurations:
#             1. conf_args[0] is obj -> True,
#             2. *conf_args=(<class '__main__.xClass'>,), *conf_kwargs=={}
#   xClass.__new__(
#             cls=<class '__main__.xClass'>,
#             arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass:
#             arg=MISSING, kw_arg=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}> to __init__
#   xClass.__init__(
#             self=<an Instance of xClass, named xClass:
#             arg=MISSING, kw_arg=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}>,
#             arg=pos_arg, kw_arg=None)
# w returns <an Instance of xClass, named xClass:
#             arg=pos_arg, kw_arg=None,
#             **instance-attributes={'kw_arg': None, 'arg': 'pos_arg', '_attrs': ['A', 'B']}>
#   decorator(*conf_args=(), **conf_kwargs={}
#   decorator.decorator_(
#             obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg',), **kwargs={}
#   -- decorator was given following configurations:
#             1. conf_args[0] is obj -> False,
#             2. *conf_args=(), *conf_kwargs=={}
#   xClass.__new__(
#             cls=<class '__main__.xClass'>,
#             arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass:
#             arg=MISSING, kw_arg=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}> to __init__
#   xClass.__init__(
#             self=<an Instance of xClass, named xClass:
#             arg=MISSING, kw_arg=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}>,
#             arg=pos_arg, kw_arg=None)
# x returns <an Instance of xClass, named xClass:
#             arg=pos_arg, kw_arg=None,
#             **instance-attributes={'kw_arg': None, 'arg': 'pos_arg', '_attrs': ['A', 'B']}>
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'dec_config': {'change_name': 'Hello world!'}}
#   decorator.decorator_(
#             obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg', 'kw_arg'), **kwargs={}
#   -- decorator was given following configurations:
#             1. conf_args[0] is obj -> False,
#             2. *conf_args=('dec_posarg',), *conf_kwargs=={'dec_config': {'change_name': 'Hello world!'}}
#   xClass.__new__(
#             cls=<class '__main__.xClass'>,
#             arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'Hello world!'>, <Hello world! object>>
#   --- dispatching <an Instance of xClass, named Hello world!:
#             arg=MISSING, kw_arg=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}> to __init__
#   xClass.__init__(
#             self=<an Instance of xClass, named Hello world!:
#             arg=MISSING, kw_arg=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}>,
#             arg=pos_arg, kw_arg=kw_arg)
# y returns <an Instance of xClass, named Hello world!:
#             arg=pos_arg, kw_arg=kw_arg,
#             **instance-attributes={'kw_arg': 'kw_arg', 'arg': 'pos_arg', '_attrs': ['A', 'B']}>
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'dec_config': {'alternative': 'AlternativeClass'}}
#   decorator.decorator_(
#             obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg', 'kw_arg'), **kwargs={}
#   -- decorator was given following configurations:
#             1. conf_args[0] is obj -> False,
#             2. *conf_args=('dec_posarg',), *conf_kwargs=={'dec_config': {'alternative': 'AlternativeClass'}}
#   xClass.__new__(
#             cls=<class '__main__.xClass'>,
#             arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'Hello world!'>, <Hello world! object>>
#   --- dispatching <__main__.AlternativeClass object at 0x1034d92e8> directly, without __init__ invocation
#   decorator.decorator_.wrapper(
#             decorator has modified underlying object. It's a mutation.
# z returns <__main__.AlternativeClass object at 0x1034d92e8>