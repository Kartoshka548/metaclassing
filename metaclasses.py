class Meta(type):
    """
    By convention, when defining metaclasses cls is used rather than self
    as the first argument to all methods EXCEPT __prepare__ & __new__(there's no class yet...)
    (which uses mcs, for reasons explained later).

    cls is the class object that is being modified.
    """
    @classmethod
    def __prepare__(mcs, name, bases, **configs):
        """
        This attribute is invoked as a function before the evaluation of the class body.
        It takes two positional arguments, and an arbitrary number of keyword arguments.
        The two positional arguments are:
           'name' - the name of the class being created.
           'bases' - the list of base classes.

        The interpreter always tests for the existence of __prepare__ before calling it;
        If it is not present, then a regular empty dictionary is used.

        Typically, __prepare__ will create a custom dictionary - either a subclass of dict,
        or a wrapper around it - that will contain ADDITIONAL PROPERTIES that are set either before or
        during the evaluation of the class body. Then in the second phase, the metaclass can use these
        additional properties to further customize the class.

        When __prepare__ is called, metaclass itself is not yet instantiated. That means,
        if it were an ordinary method with self as the first parameter - there would be no value to
        become the self in this call. Although it's possible to implement __prepare__ as a staticmethod,
        it would be unable to access any other methods or the metaclass, which is unnecessarily
        limiting. super() will have to break inheritance chain as as there will be nothing to super from.

        Class decorators can not replace the default dictionary but __prepare__ could.
        __prepare__ has no effect when defined in regular classes - it isn't called.
        """
        _a = (mcs, name, bases, configs)
        _fmt = 'mcs=%s, name=%r, bases=%s, **%s' % _a
        print('  Meta.__prepare__(%s)' % _fmt)
        conf = configs.get('config')
        # ignoring inheritance: return plain {}, without calling on super()
        return conf and {'c': 3} or super().__prepare__(name, bases, **configs)

    def __new__(mcs, name, bases, attrs, **configs):
        """
        Meta.__new__ is used to create <instances of Meta which is a xClass object>
        The __new__ method is THE constructor (produces new, bare instance to be initialized by __init__).

        DO NOT send "**kwargs" to type.__new__
        It won't catch them and will raise a TypeError: type() takes 1 or 3 arguments" exception.
        """
        _a = (mcs, name, bases, ', '.join(attrs), configs)
        _fmt = 'mcs=%s, name=%r, bases=%s, attrs=[%s], **%s' % _a
        print('  Meta.__new__(%s)' % _fmt)

        # super() is the same as super(__class__, <first argument>),
        # super() ==  super(__class__, mcs)                        -> False
        # super().__class__ == super(__class__, mcs).__class__     -> True (<class 'super'>)
        metasuper = super()  # <super: <class 'Meta'>, <Meta object>>
        print('  - Meta.__new__(): call to Meta super() returns %s' % metasuper)
        _q = metasuper.__new__(mcs, name, bases, attrs)
        print('  - Meta.__new__(): returning %s' % _q)
        non_magic_methods = (m for m in dir(_q) if not m.startswith('__'))
        print('  - Meta.__new__(): %s has %s attrs' % (_q, {k: getattr(_q, k) for k in non_magic_methods}))
        return _q

    def __init__(cls, name, bases, attrs, **configs):
        """
        The instance is already constructed by __new__ when __init__ is called.

        DO NOT forward *configs* to type.__init__
        type won't get'em them but raise TypeError: "type.__init__() takes NO keyword arguments".
        """
        _a = (cls, name, bases, ', '.join(attrs), configs)
        _fmt = 'cls=%s, name=%r, bases=%s, attrs=[%s], **%s)' % _a
        print('  Meta.__init__(%s)' % _fmt)
        return super().__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        """
        xClass already exists -> class creation configuration params are redundant (and excluded).
        It's a different breed of __magic__. The args it's passed to are the same as for xClass.
        """
        _fmt = 'cls=%s, args=%s, kwargs=%s' % (cls, args, kwargs)
        print()
        print('  {:*<135}'.format('Meta.__call__(%s)' % _fmt))
        return super().__call__(*args, **kwargs)

    def __str__(cls):
        return '<an Instance of Meta: %s>' % repr(cls)


class xClass(object, metaclass=Meta, config=1):
    """
    For magic methods the lookup is always done on the class.

    class MyClass(metaclass=MyMetaClass) gets translated into
    MyClass = MyMetaClass(name, bases, **kwargs) - it's a MyMetaClass instance.

    Configuring class creation achieved by sending keyword arguments to it's metaclass.
    # procedure (M-metaclass,C-class) -> M:pni - M:cC:nic
    """
    a, b = 1, 2
    def __new__(cls, myarg, altclass=None):
        """
        cls.__new__ is used to create instances of cls.
        It's a staticmethod with first argument => cls, where
        return value of __new__() will a new Instance (usually an instance of cls).

        Create a new instance of the class by invoking the superclass’s __new__() method
        using super(currentclass, cls).__new__(cls [, ...]), which is the same as super(cls, cls).__new__(cls)
        #>> <__main__.xClass object at 0xMemAddr>, and then modify newly created class (instance of Meta) if needed.

        IMPORTANT: If __new__() DOES NOT RETURN AN_INSTANCE_OF_cls ->  __init__ WILL NOT BE INVOKED.
        (because, newly created object may not have an __init__ method defined)

        MAINLY, __new__ IS INTENDED TO ALLOW IMMUTABLE TYPE (INT, STR, TUPLE) SUBCLASSES TO CUSTOMIZE INSTANCE CREATION.
        It is also commonly overridden in metaclasses in order to customize class creation.

        When the class defines __new__, it will be looked up on the same object (the class),
        not on a upper level (in a metaclass or parent object) like all the rest of magic methods.
        This is important to understand, because both the class and the metaclass can define this method.
        """
        _fmt = 'cls=%s, myarg=%s, altclass=%s' % (cls, myarg, altclass)
        print('  xClass.__new__(%s)' % _fmt)

        if altclass is not None:
            #  super(), super(__class__, cls), ->  superclass is a wrapper around cls
            #  super().__new__(cls)  ->  <__main__.xClass object at 0xMemAddr>
            #  object.__new__(cls) ->  <__main__.xClass object at 0xMemAddr>
            #  super().__self_class__ == super().__thisclass__ == cls -> True  # wrapped object
            _super = super()  # -> <super: <class 'xClass'>, <xClass object>>
            print('  - xClass.__new__(): call to super() returns %s' % _super)
            obj = _super.__new__(cls)
            desc = 'to __init__' # internally, isinstance(obj, cls) check is performed
        else:
            obj = {'key': 'value', 'self': None}
            desc = 'directly, without __init__ invocation'
        print('  - xClass.__new__(): dispatching %s %s' % (obj, desc))
        return obj  # Not returning an instance of an xClass? __init__ will be skipped

    def __init__(self, myarg, altclass=None):
        """
        Received an instance created in __new__
        Remaining arguments *are the same* as were passed to __new__
        """
        _fmt = 'self=%s, myarg=%s, altclass=%s' % (self, myarg, altclass)
        print('  xClass.__init__(%s)' % _fmt)
        self.myarg = myarg
        self.altclass = altclass
        return super().__init__()

    def __str__(self):
        _fmt = '<an Instance of xClass; myargs=%s, altclass=%s>'
        _args = getattr(self, 'myarg', 'MISSING'), getattr(self, 'altclass', 'MISSING')
        return _fmt % _args

print(xClass('posarg', altclass=dict))
print(xClass('posarg'))
print('\ntype(xClass) == Meta: %s, type(xClass): %s' % (type(xClass) == Meta, type(xClass)))

#   Meta.__prepare__(mcs=<class '__main__.Meta'>,
#                    name='xClass',
#                    bases=(<class 'object'>,),
#                    **{'config': 1})
#   Meta.__new__(mcs=<class '__main__.Meta'>,
#                name='xClass',
#                bases=(<class 'object'>,),
#                attrs=[__doc__,__qualname__, __new__, __str__, __module__, __init__,  a, b, c],
#                **{'config': 1})
#   - Meta.__new__(): call to Meta super() returns <super: <class 'Meta'>, <Meta object>>
#   - Meta.__new__(): returning <an Instance of a Meta: <class '__main__.xClass'>>
#   - Meta.__new__(): <an Instance of Meta: <class '__main__.xClass'>> has {'a': 1, 'c': 3, 'b': 2} attrs
#   Meta.__init__(cls=<an Instance of Meta: <class '__main__.xClass'>>,
#                 name='xClass',
#                 bases=(<class 'object'>,),
#                 attrs=[__doc__, __qualname__, __new__, __str__, __module__, __init__, a, b, c],
#                 **{'config': 1}))
#
# *******************************************************************************************
#   Meta.__call__(cls=<an Instance of Meta: <class '__main__.xClass'>>,
#                 args=('posarg',),
#                 kwargs={'altclass': <class 'dict'>})
#   xClass.__new__(cls=<an Instance of Meta: <class '__main__.xClass'>>,
#                  myarg=posarg,
#                  altclass=<class 'dict'>)
#   - xClass.__new__(): call to super() returns <super: <class 'xClass'>, <xClass object>>
#   - xClass.__new__(): dispatching <an Instance of xClass; myargs=MISSING, altclass=MISSING> to __init__
#   xClass.__init__(self=<an Instance of xClass;
#                   myargs=MISSING, altclass=MISSING>,
#                   myarg=posarg,
#                   altclass=<class 'dict'>)
# >>> <an Instance of xClass; myargs=posarg, altclass=<class 'dict'>>

# *******************************************************************************************
#   Meta.__call__(cls=<an Instance of a Meta: <class '__main__.xClass'>>,
#                 args=('posarg',),
#                 kwargs={})
#   xClass.__new__(cls=<an Instance of a Meta: <class '__main__.xClass'>>,
#                  myarg=posarg,
#                  altclass=None)
#   - xClass.__new__(): call to super() returns <super: <class 'xClass'>, <xClass object>>
#   - xClass.__new__(): dispatching {'key': 'value', 'self': None} directly, without __init__ invocation
# >>> {'key': 'value', 'self': None}
#
# type(xClass) == Meta: True, type(xClass): <class '__main__.Meta'>