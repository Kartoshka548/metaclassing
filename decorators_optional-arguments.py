def decorator(*conf_args, **conf_kwargs):
    """
    Decorator which may be called with or without configuration arguments, like so:
        1. @decorator, translated into
             -> decorator(func)(*args, **kwargs)
        2. @decorator(*conf_args, **conf_kwargs), translated into
             -> decorator(*conf_args, **conf_kwargs)(func)(*args, **kwargs)
    """
    confs = conf_args, conf_kwargs
    sp = chr(32)*12
    args_ = chr(32)*2, *confs
    print('%sdecorator(*conf_args=%s, **conf_kwargs=%s' % args_)
    def decorator_(obj):
        """
        Logging decorator for API methods,
        Logging in and out params per method called.
        """
        print('  decorator.decorator_(obj=%s' % obj)

        def wrapper(*args, **kwargs):
            """
            Each time there's a new instantiation,
            this wrapper, representing an obj which it holds, is called.
            """
            _args = args, kwargs
            args_ = chr(95)*90, chr(32)*2, *_args
            print('{}\n{}decorator.decorator_.wrapper(\n{sp}*args={}, **kwargs={})'.format(*args_, sp=sp))

            slice_start = (2, 0)[configured]
            slice_obj = slice(slice_start, slice_start+2)
            cfg = ("", "following", "NOT ", "any")[slice_obj] + (len(conf_args) > 0 and conf_args[0] is obj,)

            print('  -- decorator was {}given {} configurations:\n{sp}1. conf_args[0] is obj -> {},'
                  '\n{sp}2. *conf_args={}, *conf_kwargs=={}'.format(*cfg, *confs, sp=sp))

            # if decorator was 'configured'
            dec_config = conf_kwargs.get('dec_config', {})
            alternative = dec_config.get('alternative')
            alternative_name = dec_config.get('change_name')

            if alternative:
                # trojan planted
                # __new__ will construct something else than instance of it's cls
                # __init__ will not be called (as it won't make any sense)
                setattr(obj, 'change_name', alternative)

            elif alternative_name:
                obj.__name__ = alternative_name

            result = obj(*args, **kwargs)

            # id() or its equivalent is used in the is operator,
            # "An integer (or long) guaranteed to be unique and constant for this object during its lifetime."
            # CPython implementation compares the memory address an object resides in.
            if not result.__class__ is obj:
                print('{}decorator.decorator_.wrapper(\n{sp}'
                      'ALARM! It\'s a mutation, object has been compromised!'.format(chr(32)*2, sp=sp))

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

    _sp = '%s%s' % (chr(10), (chr(32)*8))

    def __new__(cls, arg, kw_arg=None):
        args_ = arg, kw_arg
        _fmt = chr(32)*2, '{sp}cls={},{sp}arg={}, kw_arg={}'.format(cls, *args_, sp=cls._sp)
        print('%sxClass.__new__(%s)' % _fmt)

        _super = super()
        print('  --- call to super() returns %s' % _super)

        # If decorator defined alternative name,
        # create <a: new empty class named alternative name>
        # Return either untouched or the one with altered name.
        change_name = getattr(cls, 'change_name', None)
        if change_name:
            # return predefined class with alternative name given
            str_ = lambda self: '%s (instance of %s)' % (self.__class__.__name__, self.__class__)
            obj = _super.__new__(type(change_name, (object,), {'__str__': str_}))
            desc = 'directly, without __init__ invocation'
        else:
            obj = _super.__new__(cls)
            desc = 'to __init__'

        # internally, isinstance(obj, cls) is performed before __init__
        # if __new__ returns other than an instance of a cls, __init__ will be skipped
        print('  --- dispatching %s %s' % (obj, desc))
        return obj

    def __init__(self, arg, kw_arg=None):

        # Declaration below will initialize self. Keep out.
        # args_ = self.arg, self.kw_arg = arg, kw_arg
        args_ = arg, kw_arg
        _fmt = chr(32)*2, '{sp}self={},{sp}arg={}, kw_arg={}'.format(self, *args_, sp=self._sp)
        print('%sxClass.__init__(%s)' % _fmt)
        self.arg, self.kw_arg = args_
        return super().__init__()

    def __str__(self):
        attrs = dict((k, getattr(self, k)) for k in dir(self) if not (k.startswith(chr(95)*2) or k in ('_sp',)))
        _args = self.__class__.__name__, getattr(self, 'arg', 'MISSING'), \
                getattr(self, 'kw_arg', 'MISSING'), attrs
        return '<an Instance of xClass, named {} with{sp}arg={}, ' \
               'kw_arg={},{sp}**instance-attributes={}>'.format(*_args, sp=self._sp)


#### FLIGHT
########################
spacer = chr(94)*90
change_name = dict(change_name="Robert'); DROP TABLE Students; --S0\u042F\u042FY \u2603")
alternative = dict(alternative='AlternativeClass')

#fp
UseCase = __import__('collections').namedtuple('uc', 'description obj')
#OOP
# from collections import namedtuple
# class Usecase(namedtuple('uc', ['description', 'obj'])): pass

decorators = (
    # @decorator - no args
    # this decorator will return <instance of decorated object>
    UseCase("decorator(xClass)('pos_arg')",
        lambda: decorator(xClass)('pos_arg')),

    # @decorator() - empty args
    # same as above
    UseCase("decorator()(xClass)('pos_arg')",
        lambda: decorator()(xClass)('pos_arg')),

    # @decorator(arg1, arg2) - modifying class' name
    # this decorator will return <instance of original object, named differently>
    UseCase("decorator('dec_posarg', dec_config=%s"
                "(xClass)('pos_arg', 'kw_arg')" % str(change_name),
        lambda: decorator('dec_posarg', dec_config=change_name)(xClass)('pos_arg', 'kw_arg')),

    # @decorator(arg1, arg2) - returning alternative object
    # this decorator will return <instance of another class>
    UseCase("decorator('dec_posarg', dec_config=%s)"
                "(xClass)('pos_arg', 'kw_arg')" % str(alternative),
        lambda: decorator('dec_posarg', dec_config=alternative)(xClass)('pos_arg', 'kw_arg')))

for desc, dec in decorators:
    print('%s\n+++ TRYING %s\n' % (spacer, desc))
    print("+++ RESULT: %s" % dec())


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING decorator(xClass)('pos_arg')
#
#   decorator(*conf_args=(<class '__main__.xClass'>,), **conf_kwargs={}
#   decorator.decorator_(obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg',), **kwargs={})
#   -- decorator was NOT given any configurations:
#             1. conf_args[0] is obj -> True,
#             2. *conf_args=(<class '__main__.xClass'>,), *conf_kwargs=={}
#   xClass.__new__(
#         cls=<class '__main__.xClass'>,
#         arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass with
#         arg=MISSING, kw_arg=MISSING,
#         **instance-attributes={}> to __init__
#   xClass.__init__(
#         self=<an Instance of xClass, named xClass with
#         arg=MISSING, kw_arg=MISSING,
#         **instance-attributes={}>,
#         arg=pos_arg, kw_arg=None)
# +++ RESULT: <an Instance of xClass, named xClass with
#         arg=pos_arg, kw_arg=None,
#         **instance-attributes={'kw_arg': None, 'arg': 'pos_arg'}>
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING decorator()(xClass)('pos_arg')
#
#   decorator(*conf_args=(), **conf_kwargs={}
#   decorator.decorator_(obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg',), **kwargs={})
#   -- decorator was given following configurations:
#             1. conf_args[0] is obj -> False,
#             2. *conf_args=(), *conf_kwargs=={}
#   xClass.__new__(
#         cls=<class '__main__.xClass'>,
#         arg=pos_arg, kw_arg=None)
#   --- call to super() returns <super: <class 'xClass'>, <xClass object>>
#   --- dispatching <an Instance of xClass, named xClass with
#         arg=MISSING, kw_arg=MISSING,
#         **instance-attributes={}> to __init__
#   xClass.__init__(
#         self=<an Instance of xClass, named xClass with
#         arg=MISSING, kw_arg=MISSING,
#         **instance-attributes={}>,
#         arg=pos_arg, kw_arg=None)
# +++ RESULT: <an Instance of xClass, named xClass with
#         arg=pos_arg, kw_arg=None,
#         **instance-attributes={'kw_arg': None, 'arg': 'pos_arg'}>
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING decorator('dec_posarg', dec_config={'change_name': "Robert'); DROP TABLE Students; --S0ЯЯY ☃"}(xClass)('pos_arg', 'kw_arg')
#
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'dec_config': {'change_name': "Robert'); DROP TABLE Students; --S0ЯЯY ☃"}}
#   decorator.decorator_(obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg', 'kw_arg'), **kwargs={})
#   -- decorator was given following configurations:
#             1. conf_args[0] is obj -> False,
#             2. *conf_args=('dec_posarg',), *conf_kwargs=={'dec_config': {'change_name': "Robert'); DROP TABLE Students; --S0ЯЯY ☃"}}
#   xClass.__new__(
#         cls=<class '__main__.xClass'>,
#         arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'Robert'); DROP TABLE Students; --S0ЯЯY ☃'>, <Robert'); DROP TABLE Students; --S0ЯЯY ☃ object>>
#   --- dispatching <an Instance of xClass, named Robert'); DROP TABLE Students; --S0ЯЯY ☃ with
#         arg=MISSING, kw_arg=MISSING,
#         **instance-attributes={}> to __init__
#   xClass.__init__(
#         self=<an Instance of xClass, named Robert'); DROP TABLE Students; --S0ЯЯY ☃ with
#         arg=MISSING, kw_arg=MISSING,
#         **instance-attributes={}>,
#         arg=pos_arg, kw_arg=kw_arg)
# +++ RESULT: <an Instance of xClass, named Robert'); DROP TABLE Students; --S0ЯЯY ☃ with
#         arg=pos_arg, kw_arg=kw_arg,
#         **instance-attributes={'kw_arg': 'kw_arg', 'arg': 'pos_arg'}>
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# +++ TRYING decorator('dec_posarg', dec_config={'alternative': 'AlternativeClass'})(xClass)('pos_arg', 'kw_arg')
#
#   decorator(*conf_args=('dec_posarg',), **conf_kwargs={'dec_config': {'alternative': 'AlternativeClass'}}
#   decorator.decorator_(obj=<class '__main__.xClass'>
# __________________________________________________________________________________________
#   decorator.decorator_.wrapper(
#             *args=('pos_arg', 'kw_arg'), **kwargs={})
#   -- decorator was given following configurations:
#             1. conf_args[0] is obj -> False,
#             2. *conf_args=('dec_posarg',), *conf_kwargs=={'dec_config': {'alternative': 'AlternativeClass'}}
#   xClass.__new__(
#         cls=<class '__main__.xClass'>,
#         arg=pos_arg, kw_arg=kw_arg)
#   --- call to super() returns <super: <class 'Robert'); DROP TABLE Students; --S0ЯЯY ☃'>, <Robert'); DROP TABLE Students; --S0ЯЯY ☃ object>>
#   --- dispatching AlternativeClass (instance of <class '__main__.AlternativeClass'>) directly, without __init__ invocation
#   decorator.decorator_.wrapper(
#             ALARM! It's a mutation, object has been compromised!
# +++ RESULT: AlternativeClass (instance of <class '__main__.AlternativeClass'>)