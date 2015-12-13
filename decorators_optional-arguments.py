from collections import namedtuple

UseCase = namedtuple('uc', 'description obj')  # same as `class UseCase(namedtuple(...)): pass`
case_spacer, hairline = (chr(c)*90 for c in (94, 95))
sp_short, sp = chr(32)*2, chr(32)*6


def decorator(*conf_args, **conf_kwargs):
    """
    Decorator which may be called with or without configuration arguments, like so:
        1. @decorator, translated into
             -> decorator(func)(*args, **kwargs)
        2. @decorator(*conf_args, **conf_kwargs), translated into
             -> decorator(*conf_args, **conf_kwargs)(func)(*args, **kwargs)
    """
    confs = conf_args, conf_kwargs
    print('%sdecorator(*conf_args=%s, **conf_kwargs=%s)' % (sp_short, *confs))

    def decorator_(obj):
        """
        This layer of decoration does gatekeeping only,
        allowing exposed decorator layer (previous frame) to _optionally_ accept arguments.
        It is executed:
            - immediately in case of no-args decorator, where obj is implicitly the only argument.
            - after args processed/memoized within previous layer, and obj is now passed explicitly.
        """
        print('%sdecorator.decorator_(obj=%s)' % (sp_short, obj))

        arg_is_obj = conf_args and conf_args[0] is obj or False
        slice_start = arg_is_obj and 3 or 0
        slice_obj = slice(slice_start, slice_start+3)
        cfg = ("", "", "meaning", "not ", "any ", "so")[slice_obj] + (arg_is_obj,)
        print('{}-- decorator was {}called with {}configurations {} '
              'conf_args[0] is obj -> {}'.format(sp_short, *cfg, *confs))

        def wrapper(*args, **kwargs):
            """
            Each time there's a new instantiation,
            this wrapper, representing an obj which it holds, is called.
            """
            print('{}\n{}decorator.decorator_.wrapper(\n'
                  '{sp}*args={}, **kwargs={})'.format(hairline, sp_short, args, kwargs, sp=sp))

            nonlocal obj
            # modifying obj should not have any effect on other obj instances
            original_obj = obj

            # if decorator was 'configured'
            dec_config = conf_kwargs.get('dec_config') or conf_kwargs # allowing skipping on dec_conf
            alternative = dec_config.get('alternative')
            change_name = dec_config.get('change_name')

            # proper OOP inheritance will have the class created at local namespace, not what we want
            # <class '__main__.decorator.<locals>.decorator_.<locals>.wrapper.<locals>._bj'>
            if alternative:
                obj = type(obj.__name__, (obj,), {'alternative_obj': alternative})
            elif change_name:
                obj = type(change_name, (obj,), {})
            result = obj(*args, **kwargs)

            # id() or its equivalent is used in the is operator,
            # "An integer (or long) guaranteed to be unique and constant for this object during its lifetime."
            # CPython implementation compares the memory address an object resides in.
            if result.__class__ is not original_obj:
                print('{}decorator.decorator_.wrapper(\n'
                      '{sp}ALARM! It\'s a mutation, object has been compromised!'.format(sp_short, sp=sp))
            return result
        return wrapper

    if (len(conf_args) == 1          # decorating a function, a class or a method
        and callable(*conf_args)    # must be top-level callable - @decorator() w/o args will be left out
        and not conf_kwargs):       # must not have anything else accompanying

        # was called as @decorator -> decorator(obj) with obj as the _only_ argument
        # manually enforce calling next layer of wrapping
        # stay identical after that when actual instantiation happens
        return decorator_(*conf_args)

    else:

        # @decorator(...) -> decorator(*conf_args, **conf_kwargs)(func)
        # decorator was called with config arguments; return normal layer of wrapping
        # next call will provide the decorator_ with an obj.
        # It was manually enforced in the technique above.
        return decorator_


class xClass(object):
    _sp = '%s%s' % (chr(10), sp)

    def __new__(cls, arg, kw_arg=None):
        print('{}xClass.__new__({sp}cls={},{sp}arg={}, kw_arg={})'.format(
            sp_short, cls, arg, kw_arg, sp=cls._sp))

        _super = super()
        print('{}--- call to super() returns {}'.format(sp_short, _super))

        # If decorator defined alternative_obj,
        # create <a: new empty class named alternative_obj as it's name>
        # Return the latter or untouched.
        alternative_obj = getattr(cls, 'alternative_obj', None)

        if alternative_obj:

            # __new__ will construct something else than instance of it's cls
            # __init__ will not be called (as it won't make any sense)
            # return predefined alternative class with given name
            str_ = lambda self: '%s (instance of %s)' % (self.__class__.__name__, self.__class__)
            obj = _super.__new__(type(alternative_obj, (object,), {'__str__': str_}))
            desc = 'directly, without __init__ invocation'

        else:

            obj = _super.__new__(cls)
            desc = 'to __init__'

        # internally, isinstance(obj, cls) is performed before __init__
        # if __new__ returns other than an instance of a cls, __init__ will be skipped
        print('%s--- dispatching %s %s' % (sp_short, obj, desc))
        return obj


    def __init__(self, arg, kw_arg=None):
        # Declaration below will initialize instance.
        # args_ = self.arg, self.kw_arg = arg, kw_arg
        args_ = arg, kw_arg
        _fmt = sp_short, '{sp}self={},{sp}arg={}, kw_arg={}'.format(self, *args_, sp=self._sp)
        print('%sxClass.__init__(%s)' % _fmt)
        self.arg, self.kw_arg = args_
        return super().__init__()


    def __str__(self):
        _args = self.__class__.__name__, getattr(self, 'arg', 'MISSING'), \
                getattr(self, 'kw_arg', 'MISSING'), self.__dict__
        return '<an Instance of xClass, named {} with{sp}arg={}, ' \
               'kw_arg={},{sp}**instance-attributes={}>'.format(*_args, sp=self._sp)


#### FLIGHT
########################
conf = {
    'altered_name': {
        'change_name': "Robert'); DROP TABLE Students; --S0\u042F\u042FY \u2603"},
    'different_object': {
        'alternative': 'AlternativeClass'},
    'direct_drop': {
        'alternative': 'NotFrom-dec_config'}}
desc_ = {
    'dec':  "%s@decorator" % sp,
    'cls':  "%sclass xClass(object): ...\n" % sp,
    'xcls': "%s>>>xClass('pos_arg'" % sp}

# to decorate same base class with different decorator settings,
# an inline decoration is required.
decorators = (

    # this decorator and next will both return <instance of decorated object>
    # decorator(xClass)('pos_arg')
    UseCase(
        obj=lambda: decorator(xClass)('pos_arg'),
        description="\n%(dec)s\n%(cls)s"
                    "%(xcls)s)" % desc_),

    # decorator()(xClass)('pos_arg')
    UseCase(
        obj=lambda: decorator()(xClass)('pos_arg'),
        description="\n%(dec)s()\n%(cls)s%(xcls)s)" % desc_),

    # decorator('dec_posarg')(xClass)('pos_arg')
    UseCase(
        obj=lambda: decorator('dec_posarg')(xClass)('pos_arg'),
        description="\n%(dec)s('dec_posarg')\n%(cls)s%(xcls)s)" % desc_),

    # this decorator will return <instance of original object, named differently>
    # decorator('dec_posarg', dec_config={'change_name': ...})(xClass)(...)
    UseCase(
        obj=lambda: decorator('dec_posarg',
            dec_config=conf['altered_name'])(xClass)('pos_arg', 'kw_arg'),
        description="\n%(dec)s('dec_posarg', "
                    "dec_config=%(conf)s)\n%(cls)s"
                    "%(xcls)s, 'kw_arg')" % {
            **desc_, 'conf': str(conf['altered_name'])}),

    # this decorator will return <instance of another class>
    # decorator('dec_posarg', dec_config={'alternative': ...})(xClass)(...)
    UseCase(
        obj=lambda: decorator('dec_posarg',
            dec_config=conf['different_object'])(xClass)('pos_arg', 'kw_arg'),
        description="\n%(dec)s('dec_posarg', "
                    "dec_config=%(conf)s)\n%(cls)s"
                    "%(xcls)s, 'kw_arg')" % {
            **desc_, 'conf': str(conf['different_object'])}),

    # this decorator will return <instance of another class>
    # decorator('dec_posarg', dec_config={'alternative': ...})(xClass)(...)
    UseCase(
        obj=lambda: decorator('dec_posarg',
            **conf['direct_drop'])(xClass)('pos_arg', 'kw_arg'),
        description="\n%(dec)s('dec_posarg', "
                    "%(conf)s)\n%(cls)s"
                    "%(xcls)s, 'kw_arg')" % {
            **desc_, 'conf': ', '.join("{!s}={!r}".format(key,val) for (key,val) in conf['direct_drop'].items())}))


for uc in decorators:
    print('%s\n+++ TRYING %s\n' % (case_spacer, uc.description))
    print("+++ RESULT: %s\n%s" % (uc.obj(), hairline))



# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING
#       @decorator
#       class xClass(object): ...
#       >>>xClass('pos_arg')
#
#   decorator(*conf_args=(<class '__main__.xClass'>,), **conf_kwargs={})
#   decorator.decorator_(obj=<class '__main__.xClass'>)
#   -- decorator was not called with any configurations so conf_args[0] is obj -> True
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#       *args=('pos_arg',), **kwargs={})
#   xClass.__new__(
#       cls=<class '__main__.xClass'>,
#       arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}> to __init__
#   xClass.__init__(
#       self=<an Instance of xClass, named xClass with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}>,
#       arg=pos_arg, kw_arg=None)
# +++ RESULT: <an Instance of xClass, named xClass with
#       arg=pos_arg, kw_arg=None,
#       **instance-attributes={'arg': 'pos_arg', 'kw_arg': None}>
# __________________________________________________________________________________________
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING
#       @decorator()
#       class xClass(object): ...
#       >>>xClass('pos_arg')
#
#   decorator(*conf_args=(), **conf_kwargs={})
#   decorator.decorator_(obj=<class '__main__.xClass'>)
#   -- decorator was called with configurations meaning conf_args[0] is obj -> False
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#       *args=('pos_arg',), **kwargs={})
#   xClass.__new__(
#       cls=<class '__main__.xClass'>,
#       arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}> to __init__
#   xClass.__init__(
#       self=<an Instance of xClass, named xClass with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}>,
#       arg=pos_arg, kw_arg=None)
# +++ RESULT: <an Instance of xClass, named xClass with
#       arg=pos_arg, kw_arg=None,
#       **instance-attributes={'arg': 'pos_arg', 'kw_arg': None}>
# __________________________________________________________________________________________
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING
#       @decorator('dec_posarg')
#       class xClass(object): ...
#       >>>xClass('pos_arg')
#
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={})
#   decorator.decorator_(obj=<class '__main__.xClass'>)
#   -- decorator was called with configurations meaning conf_args[0] is obj -> False
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#       *args=('pos_arg',), **kwargs={})
#   xClass.__new__(
#       cls=<class '__main__.xClass'>,
#       arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}> to __init__
#   xClass.__init__(
#       self=<an Instance of xClass, named xClass with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}>,
#       arg=pos_arg, kw_arg=None)
# +++ RESULT: <an Instance of xClass, named xClass with
#       arg=pos_arg, kw_arg=None,
#       **instance-attributes={'arg': 'pos_arg', 'kw_arg': None}>
# __________________________________________________________________________________________
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING
#       @decorator('dec_posarg', dec_config={'change_name': "Robert'); DROP TABLE Students; --S0ЯЯY ☃"})
#       class xClass(object): ...
#       >>>xClass('pos_arg', 'kw_arg')
#
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'dec_config': {'change_name': "Robert'); DROP TABLE Students; --S0ЯЯY ☃"}})
#   decorator.decorator_(obj=<class '__main__.xClass'>)
#   -- decorator was called with configurations meaning conf_args[0] is obj -> False
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#       *args=('pos_arg', 'kw_arg'), **kwargs={})
#   xClass.__new__(
#       cls=<class '__main__.Robert'); DROP TABLE Students; --S0ЯЯY ☃'>,
#       arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'xClass'>, <Robert'); DROP TABLE Students; --S0ЯЯY ☃ object>>
#   --- dispatching <an Instance of xClass, named Robert'); DROP TABLE Students; --S0ЯЯY ☃ with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}> to __init__
#   xClass.__init__(
#       self=<an Instance of xClass, named Robert'); DROP TABLE Students; --S0ЯЯY ☃ with
#       arg=MISSING, kw_arg=MISSING,
#       **instance-attributes={}>,
#       arg=pos_arg, kw_arg=kw_arg)
#   decorator.decorator_.wrapper(
#       ALARM! It's a mutation, object has been compromised!
# +++ RESULT: <an Instance of xClass, named Robert'); DROP TABLE Students; --S0ЯЯY ☃ with
#       arg=pos_arg, kw_arg=kw_arg,
#       **instance-attributes={'arg': 'pos_arg', 'kw_arg': 'kw_arg'}>
# __________________________________________________________________________________________
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING
#       @decorator('dec_posarg', dec_config={'alternative': 'AlternativeClass'})
#       class xClass(object): ...
#       >>>xClass('pos_arg', 'kw_arg')
#
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'dec_config': {'alternative': 'AlternativeClass'}})
#   decorator.decorator_(obj=<class '__main__.xClass'>)
#   -- decorator was called with configurations meaning conf_args[0] is obj -> False
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#       *args=('pos_arg', 'kw_arg'), **kwargs={})
#   xClass.__new__(
#       cls=<class '__main__.xClass'>,
#       arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching AlternativeClass (instance of <class '__main__.AlternativeClass'>) directly, without __init__ invocation
#   decorator.decorator_.wrapper(
#       ALARM! It's a mutation, object has been compromised!
# +++ RESULT: AlternativeClass (instance of <class '__main__.AlternativeClass'>)
# __________________________________________________________________________________________
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING
#       @decorator('dec_posarg', alternative='NotFrom-dec_config')
#       class xClass(object): ...
#       >>>xClass('pos_arg', 'kw_arg')
#
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'alternative': 'NotFrom-dec_config'})
#   decorator.decorator_(obj=<class '__main__.xClass'>)
#   -- decorator was called with configurations meaning conf_args[0] is obj -> False
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#       *args=('pos_arg', 'kw_arg'), **kwargs={})
#   xClass.__new__(
#       cls=<class '__main__.xClass'>,
#       arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching NotFrom-dec_config (instance of <class '__main__.NotFrom-dec_config'>) directly, without __init__ invocation
#   decorator.decorator_.wrapper(
#       ALARM! It's a mutation, object has been compromised!
# +++ RESULT: NotFrom-dec_config (instance of <class '__main__.NotFrom-dec_config'>)
# __________________________________________________________________________________________
