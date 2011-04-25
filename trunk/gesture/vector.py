'''
    Gesture Combination Authentication Program 
    submodule vectorize operation.

    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import operator
from itertools import imap, repeat
import functools
import math

iterable = lambda obj: isinstance(obj, basestring) or hasattr(obj, '__iter__')
def vector_op(op, x, y):
    if iterable(x) and iterable(y):
        return type(x)(imap(op, x, y))
    if not iterable(x):
        return type(y)(imap(op, repeat(x), y))
    if not iterable(y):
        return type(x)(imap(op, x, repeat(y)))

vector_add = functools.partial(vector_op, operator.add)
vector_sub = functools.partial(vector_op, operator.sub)
vector_mul = functools.partial(vector_op, operator.mul)
vector_div = functools.partial(vector_op, operator.div)
vector_and = functools.partial(vector_op, operator.and_)
vector_or  = functools.partial(vector_op, operator.or_)

def dot(v1,v2):
    return sum(vector_mul(v1,v2))

def norm(v1):
    return math.sqrt(dot(v1,v1))

def vector_sum(has_len):
    if not has_len:
        return has_len
    return reduce(vector_add, has_len)

def vector_mean(has_len):
    vsum = vector_sum(has_len)
    return type(vsum)(float(e)/float(len(has_len)) for e in vsum)


if __name__ == '__main__':
    positions = [(1,2,1), (3,4,3), (5,6,3)]
    print vector_sum(positions)
    print vector_mean(positions)
    print dot(positions[0], positions[1])
