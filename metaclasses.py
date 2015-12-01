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
        arguments = (mcs, name, bases, configs)
        print("""  Meta.__prepare__(\tmcs=%s,
                   \tname=%r, bases=%s,
                   \t**%s)""" % arguments)
        # in the long-term, mutating methods will have no effect  (__new__ gets the original *configs*)
        mixin = configs.get('mixin')  # [it's an inter-method immutable] - changes won't persist across calls
        if isinstance(mixin, dict):
            # if returning a tag: cls attrs will update/merge into it implicitly (see __new__'s doc)
            extra_dict = mixin.copy()  # but when returning a new object, original will stay clear
        else:
            # ignoring inheritance: return {}, without calling on super()
            extra_dict = super().__prepare__(name, bases, **configs)
        return extra_dict

    def __new__(mcs, name, bases, attrs, **configs):
        """
        metaclass.__new__ is used to create <instances of a metaclass which is a cls object>
        The __new__ method is THE constructor, producing new, bare instance to be initialized by __init__.
        param: attrs is a merged (class-attrs + what __prepare__ returned) dict object

        DO NOT send *configs* to type.__new__
        It won't catch them and will raise a TypeError: type() takes 1 or 3 arguments" exception.
        """
        arguments = (mcs, name, bases, ', '.join(attrs), configs)
        print("""  Meta.__new__(\t\tmcs=%s,
                    name=%r, bases=%s,
                    attrs=[%s],
                    **%s)""" % arguments)
        # Per instructions for cls creation, apply _attrs into actual cls attributes w/default values
        conf_attr_pointer, values = (configs.setdefault('config', {}).get(k) for k in ('attr_list', 'instruction'))
        if conf_attr_pointer in attrs and values in ('nullify',):
            attrs.update(dict.fromkeys(attrs.pop(conf_attr_pointer), 0))

        # super() is the same as super(__class__, <first argument>),
        # super() ==  super(__class__, mcs)                        -> False
        # super().__class__ == super(__class__, mcs).__class__     -> True (<class 'super'>)
        metasuper = super()  # <super: <class 'Meta'>, <Meta object>>
        print('  --- call to [mcs:Meta]\'s super() returns %s' % metasuper)
        _q = metasuper.__new__(mcs, name, bases, attrs)
        print('  --- returns %s' % _q)
        return _q

    def __init__(cls, name, bases, attrs, **configs):
        """
        The instance is already constructed by __new__ when __init__ is called.

        DO NOT forward *configs* to type.__init__
        type won't get'em them but raise TypeError: "type.__init__() takes NO keyword arguments".
        """
        # l = locals()
        # import inspect
        # arg_spec = inspect.getargspec(Meta.__init__)#inspect.currentframe().f_code.co_name)
        # _args = arg_spec.args + [arg_spec.keywords]
        # arguments = [l[a] for a in _args]

        arguments = (cls, name, bases, ', '.join(attrs), configs)
        print("""  Meta.__init__(\tcls=%s,
                    name=%r, bases=%s,
                    attrs=[%s],
                    **%s)""" % arguments)
        return super().__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        """
        xClass already exists -> class creation configuration params are redundant (and excluded).
        It's a different breed of __magic__. The args it's passed to are the same as for xClass.
        """
        print('{1}class_instantiation____\n  {0:*<135}'.format('''Meta.__call__(\tcls=%s,
                    args=%s, kwargs=%s''' % (cls, args, kwargs), chr(95)*90))
        return super().__call__(*args, **kwargs)

    def __str__(cls):
        cls_attrs = {k: getattr(cls, k) for k in dir(cls) if not k.startswith(chr(95)*2)}
        return '''<an Instance of Meta: %s,
                        **class-attributes=%s>''' % (repr(cls), cls_attrs)


class xClass(object, config=dict(attr_list='_attrs', instruction='nullify'),
             metaclass=Meta, mixin=dict(returning='*** Returning', plaindict='plain dict')):
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
print(_obj.returning, _obj)

_altered_obj = xClass('posarg', alternative_instance={'key': 'value', 'self': None})
print(xClass.returning, xClass.plaindict, _altered_obj)

print('\ntype(xClass) == Meta: %s, type(xClass): %s' % (type(xClass) == Meta, type(xClass)))

#   Meta.__prepare__(mcs=<class '__main__.Meta'>,
#                    name='xClass', bases=(<class 'object'>,),
#                    **{'config': {'attr_list': '_attrs', 'instruction': 'nullify'}, 'mixin': {'C': '*** Returning', 'D': 'plain dict'}})
#   Meta.__new__(    mcs=<class '__main__.Meta'>,
#                    name='xClass', bases=(<class 'object'>,),
#                    attrs=[__str__, __new__, __init__, C, D, __doc__, __qualname__, __module__, _attrs],
#                    **{'config': {'attr_list': '_attrs', 'instruction': 'nullify'}, 'mixin': {'C': '*** Returning', 'D': 'plain dict'}})
#   --- call to [mcs:Meta]'s super() returns <super: <class 'Meta'>, <Meta object>>
#   --- returns <an Instance of Meta: <class '__main__.xClass'>,
#                       **class-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>
#   Meta.__init__(   cls=<an Instance of Meta: <class '__main__.xClass'>,
#                       **class-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>,
#                    name='xClass', bases=(<class 'object'>,),
#                    attrs=[__str__, __new__, __init__, C, D, __doc__, A, __qualname__, __module__, B],
#                    **{'config': {'attr_list': '_attrs', 'instruction': 'nullify'}, 'mixin': {'C': '*** Returning', 'D': 'plain dict'}})
# __________________________________________________________________________________________class_instantiation____
#   Meta.__call__(   cls=<an Instance of Meta: <class '__main__.xClass'>,
#                        **class-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>,
#                    args=('posarg',), kwargs={}
#   xClass.__new__(  cls=<an Instance of Meta: <class '__main__.xClass'>,
#                        **class-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>,
#                    arg=posarg, alternative_instance=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass:
#             arg=MISSING, alternative_instance=MISSING,
#             **instance-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}> to __init__
#   xClass.__init__( self=<an Instance of xClass:
#             arg=MISSING, alternative_instance=MISSING,
#             **instance-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>,
#                    arg=posarg, alternative_instance=None)
# *** Returning <an Instance of xClass:
#             arg=posarg, alternative_instance=None,
#             **instance-attributes={'C': '*** Returning', 'D': 'plain dict', 'A': 0, 'B': 0, 'arg': 'posarg', 'alternative_instance': None}>
# __________________________________________________________________________________________class_instantiation____
#   Meta.__call__(   cls=<an Instance of Meta: <class '__main__.xClass'>,
#                        **class-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>,
#                    args=('posarg',), kwargs={'alternative_instance': {'self': None, 'key': 'value'}}
#   xClass.__new__(  cls=<an Instance of Meta: <class '__main__.xClass'>,
#                        **class-attributes={'B': 0, 'A': 0, 'C': '*** Returning', 'D': 'plain dict'}>,
#                    arg=posarg, alternative_instance={'self': None, 'key': 'value'})
#   --- dispatching {'self': None, 'key': 'value'} directly, without __init__ invocation
# *** Returning plain dict {'self': None, 'key': 'value'}
#
# type(xClass) == Meta: True, type(xClass): <class '__main__.Meta'>