import types

def decorator_with_arguments(*conf_args, **conf_kwargs):
    """
    Complete decorator logic, when instantiating decorated object 'obj' with
        obj(*args, **kwargs), translates into:
        -> decorator_accepting_arguments(*conf_args, **conf_kwargs)(obj)(*args, **kwargs)

    This part of a decorator is called ONCE at object definition,
    not on instantiation or at a runtime. It remembers (*conf_args, **conf_kwargs) arguments
    used to configure object behaviour, and returns next layer of decoration (actual 'obj' decoration).
    """
    print("""  decorator_with_arguments(
            *conf_args=%s, **conf_kwargs=%s""" % (conf_args, conf_kwargs))

    def decorator_wrapper(obj):
        """
        Wrapping used if a decorator would not accept any arguments.
        @decorator(obj) translates into decorator(obj)

        This part of a decorator is called ONCE on definition as well,
        not on instantiation or at a runtime. It remembers obj to execute and returns
        next (final) layer of wrapping which will be called each time object is executed.
        """
        print("""  -- decorator_accepting_wrapped_object(
            obj=%s""" % obj)
        def decorator(*args, **kwargs):
            """
            A wrapper around actual object, called at at EVERY execution.

            It has access to previously stored conf_args, conf_kwargs and obj,
            which are typically used here.
            """
            print(chr(95)*90, """\n  -- decorator(
            *conf_args=%s, **conf_kwargs=%s,
            *args=%s, **kwargs=%s""" % (conf_args, conf_kwargs, args, kwargs))

            mixin = conf_kwargs.get('mixin', {})

            # in case of function: <method-wrapper '__init__' of function object at 0x...>
            original__init__ = obj.__init__

            def init(self, *iargs, **ikwargs):
                print('  %s.__init__ was altered by a decorator!' % self.__class__.__name__)
                for k, v in mixin.items():
                    setattr(self, k, types.MethodType(v, self))
                original__init__(self, *iargs, **ikwargs)

            # substituting original __init__ call.
            # Not executed but *referenced* for use in call below (not applicable for functions)
            obj.__init__ = init

            # Pass control to relevant authorities: __new__ & __init__ for classes,
            # direct execution for functions.
            normal_call_result = obj(*args, **kwargs)

            if set(conf_args) & {'print__class_name', }:
                # if order of positional arguments matters, use 'v' in ('v',)
                print('  decorator: Decorated class is: %s' % normal_call_result.__class__.__name__)

            return normal_call_result
        return decorator
    return decorator_wrapper

####### FLIGHT
############################################################################################
print(chr(96)*90)

@decorator_with_arguments('print__class_name',
    mixin={'meth': lambda self: '!s% morf dlrow olleH '[::-1] % self.__class__.__name__})
class xClass(object):
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
        _fmt = """
            cls=%s,
            arg=%s, alternative_instance=%s""" % (cls, arg, alternative_instance)
        print('  xClass.__new__(%s)' % _fmt)

        if alternative_instance is not None:
            obj = alternative_instance
            desc = 'directly, without __init__ invocation'
        else:
            _super = super()
            print('  --- call to super() returns %s' % _super)
            obj = _super.__new__(cls) # needs to be a class not type
            desc = 'to __init__'
        print('  --- dispatching %s %s' % (obj, desc))
        return obj

    def __init__(self, arg, alternative_instance=None):
        """
        Received an instance created in __new__
        Remaining arguments *are the same* as were passed to __new__
        """
        _fmt = """
            self=%s,
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

_obj = xClass('posarg_A')
print('%s\n%s' % (_obj, _obj.meth()))

_altered_obj = xClass('posarg_B', alternative_instance={'key': 'value', 'self': None})
print('%s' % _altered_obj)

print(chr(96)*90)
print(chr(96)*90)

@decorator_with_arguments(
    'print__class_name', None, mixin={'meth': 'obj.__init__ will not be called (it is a function)!'})
def plain_func(a, b='abc'):
    return '%s %s' % (a, b)

print(plain_func('Also good for', 'regular functions!'))
print(chr(96)*90)


# ``````````````````````````````````````````````````````````````````````````````````````````
#   decorator_with_arguments(
#             *conf_args=('print__class_name',), **conf_kwargs={'mixin': {'meth': <function <lambda> at 0x102097950>}}
#   -- decorator_accepting_wrapped_object(
#             obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   -- decorator(
#             *conf_args=('print__class_name',), **conf_kwargs={'mixin': {'meth': <function <lambda> at 0x102097950>}},
#             *args=('posarg_A',), **kwargs={}
#   xClass.__new__(
#             cls=<class '__main__.xClass'>,
#             arg=posarg_A, alternative_instance=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass:
#             arg=MISSING, alternative_instance=MISSING,
#             **instance-attributes={}> to __init__
#   xClass.__init__ was altered by a decorator!
#   xClass.__init__(
#             self=<an Instance of xClass:
#             arg=MISSING, alternative_instance=MISSING,
#             **instance-attributes={'meth': <bound method <lambda> of <__main__.xClass object at 0x10360e390>>}>,
#             arg=posarg_A, alternative_instance=None)
#   decorator: Decorated class is: xClass
# <an Instance of xClass:
#             arg=posarg_A, alternative_instance=None,
#             **instance-attributes={'arg': 'posarg_A', 'meth': <bound method <lambda> of <__main__.xClass object at 0x10360e390>>, 'alternative_instance': None}>
#  Hello world from xClass!
# __________________________________________________________________________________________
#   -- decorator(
#             *conf_args=('print__class_name',), **conf_kwargs={'mixin': {'meth': <function <lambda> at 0x102097950>}},
#             *args=('posarg_B',), **kwargs={'alternative_instance': {'key': 'value', 'self': None}}
#   xClass.__new__(
#             cls=<class '__main__.xClass'>,
#             arg=posarg_B, alternative_instance={'key': 'value', 'self': None})
#   --- dispatching {'key': 'value', 'self': None} directly, without __init__ invocation
#   decorator: Decorated class is: dict
# {'key': 'value', 'self': None}
# ``````````````````````````````````````````````````````````````````````````````````````````
# ``````````````````````````````````````````````````````````````````````````````````````````
#   decorator_with_arguments(
#             *conf_args=('print__class_name', None), **conf_kwargs={'mixin': {'meth': 'obj.__init__ will not be called (it is a function)!'}}
#   -- decorator_accepting_wrapped_object(
#             obj=<function plain_func at 0x102097d90>
# __________________________________________________________________________________________
#   -- decorator(
#             *conf_args=('print__class_name', None), **conf_kwargs={'mixin': {'meth': 'obj.__init__ will not be called (it is a function)!'}},
#             *args=('Also good for', 'regular functions!'), **kwargs={}
#   decorator: Decorated class is: str
# Also good for regular functions!
# ``````````````````````````````````````````````````````````````````````````````````````````