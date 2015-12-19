import collections

class Status(collections.namedtuple("Status_enum", "initial prepared queued processed ready "
                                                   "discarded permission_error general_error")):
    """
    Status object with fixed values per status. available statuses are:
        - started
        - checking
        - start_after_check
        - checked
        - error
        - paused
        - queued
        - loaded
    """
    __slots__ = ()  # disabling modifications to attributes

    def __new__(cls, status=255):
        """
        Accepting optional argument which may modify inherited attributes
        and only used for that (not propagated to __init__).
        Argument has no other use and is not stored within the instance.

        Also can return base_new(cls, status & 1, status & 2, status & 4,
                             status & 8, status & 16, status & 32,
                             status & 64, status & 128)
        """
        base_new = cls.__bases__[0].__new__
        return base_new(cls, *(status & (1 << x) for x in range(0, 8)))

    def __call__(self, value):
        # status = dict(zip(self.__dict__.values(), self.__dict__.keys()))[value]
        # return '%s.%s' % (__class__.__name__, status)
        for status, numeric in self.__dict__.items():
            if not numeric == value: continue
            return '%s.%s' % (__class__.__name__, status)
        else: raise KeyError('No status with value %s found' % value)


if __name__ == '__main__':

    status = Status()
    print('128 is %s' % status(128))
    print('Status.permission_error is %d' % status.permission_error)
    print('-'*40)
    for stat in status._fields:
        print('%s: %s' % (stat, getattr(status, stat)))

# 128 is Status.general_error
# Status.permission_error is 64
# ----------------------------------------
# initial: 1
# prepared: 2
# queued: 4
# processed: 8
# ready: 16
# discarded: 32
# permission_error: 64
# general_error: 128