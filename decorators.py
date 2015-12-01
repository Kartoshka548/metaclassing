def Decorator_accepting_params(*outer_args, **outer_kwargs):
    """
    Decorator that takes arguments,
    called ONCE on definition (not on object instantiation or at function execution)

    usage: cls = outer_decorator(1, 2, 3)(cls)
    """
    print("""  Decorator_accepting_params(\n            *outer_args=%s, **outer_kwargs=%s""" % (
        outer_args, outer_kwargs))

    def decorator_accepting_wrapped_object(func):
        """
        Outermost decorator if a decorator should not accept any params
        called ONCE on definition (not on object instantiation or at function execution)
        """
        print("""  -- decorator_accepting_wrapped_object(\n            func=%s""" % func)
        def decorator_object_wrapper(*args, **kwargs):
            """
            A wrapper around actual object, called at at EVERY execution
            """
            print(chr(95)*90, """\n  -- decorator_object_wrapper(\n            *outer_args=%s, **outer_kwargs=%s,
            *args=%s, **kwargs=%s""" % (outer_args, outer_kwargs, args, kwargs))
            #do_something(*outer_args, **outer_kwargs)
            return func(*args, **kwargs)
        return decorator_object_wrapper
    return decorator_accepting_wrapped_object


@Decorator_accepting_params('dec_posarg', dec_config={'logging': 'DEBUG'})
class xClass(object):
    """
    For magic methods the lookup is always done on the class.

    class MyClass(metaclass=MyMetaClass) gets translated into
    MyClass = MyMetaClass(name, bases, **kwargs) - it's a MyMetaClass instance.

    Configuring class creation achieved by sending keyword arguments to it's metaclass.
    > Take elements in _attrs and make them class attributes with value 0
    """
    _attrs = ['A', 'B']
    def __new__(cls, arg, alternative_instance=None):
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
        _fmt = """\tcls=%s,
                    arg=%s, alternative_instance=%s""" % (cls, arg, alternative_instance)
        print('  xClass.__new__(%s)' % _fmt)

        if alternative_instance is not None:
            obj = alternative_instance
            desc = 'directly, without __init__ invocation'
        else:
            #  super(), super(__class__, cls), ->  superclass is a wrapper around cls
            #  super().__new__(cls)  ->  <__main__.xClass object at 0xMemAddr>
            #  object.__new__(cls) ->  <__main__.xClass object at 0xMemAddr>
            #  super().__self_class__ == super().__thisclass__ == cls -> True  # wrapped object
            _super = super()  # -> <super: <class 'xClass'>, <xClass object>>
            print('  --- call to super() returns %s' % _super)
            obj = _super.__new__(cls) # needs to be a class not type
            desc = 'to __init__' # internally, isinstance(obj, cls) is performed before __init__...
        print('  --- dispatching %s %s' % (obj, desc))
        return obj  # ...and if __new__ returned not an instance of a cls, __init__ will be skipped

    def __init__(self, arg, alternative_instance=None):
        """
        Received an instance created in __new__
        Remaining arguments *are the same* as were passed to __new__
        """
        _fmt = """\tself=%s,
                    arg=%s, alternative_instance=%s""" % (self, arg, alternative_instance)
        print('  xClass.__init__(%s)' % _fmt)
        self.arg = arg
        self.alternative_instance = alternative_instance
        return super().__init__()

    def __str__(self):
        # dir(self) and getattr(self, key) alternative is inspect.getmembers(self)
        attrs = dict((k, getattr(self, k)) for k in dir(self) if not k.startswith(chr(95)*2))
        _args = getattr(self, 'arg', 'MISSING'), getattr(self, 'alternative_instance', 'MISSING'), attrs
        return """<an Instance of xClass:
            arg=%s, alternative_instance=%s,
            **instance-attributes=%s>""" % _args

_obj = xClass('posarg')
print('%s' % _obj)

_altered_obj = xClass('posarg', alternative_instance={'key': 'value', 'self': None})
print('%s' % _altered_obj)



#   Decorator_accepting_params(
#             *outer_args=('dec_posarg',), **outer_kwargs={'dec_config': {'logging': 'DEBUG'}}
#   -- decorator_accepting_wrapped_object(
#             func=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   -- decorator_object_wrapper(
#             *outer_args=('dec_posarg',), **outer_kwargs={'dec_config': {'logging': 'DEBUG'}},
#             *args=('posarg',), **kwargs={}
#   xClass.__new__(	cls=<class '__main__.xClass'>,
#                     arg=posarg, alternative_instance=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass:
#             arg=MISSING, alternative_instance=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}> to __init__
#   xClass.__init__(	self=<an Instance of xClass:
#             arg=MISSING, alternative_instance=MISSING,
#             **instance-attributes={'_attrs': ['A', 'B']}>,
#                     arg=posarg, alternative_instance=None)
# <an Instance of xClass:
#             arg=posarg, alternative_instance=None,
#             **instance-attributes={'_attrs': ['A', 'B'], 'alternative_instance': None, 'arg': 'posarg'}>
# __________________________________________________________________________________________
#   -- decorator_object_wrapper(
#             *outer_args=('dec_posarg',), **outer_kwargs={'dec_config': {'logging': 'DEBUG'}},
#             *args=('posarg',), **kwargs={'alternative_instance': {'key': 'value', 'self': None}}
#   xClass.__new__(	cls=<class '__main__.xClass'>,
#                     arg=posarg, alternative_instance={'key': 'value', 'self': None})
#   --- dispatching {'key': 'value', 'self': None} directly, without __init__ invocation
# {'key': 'value', 'self': None}
