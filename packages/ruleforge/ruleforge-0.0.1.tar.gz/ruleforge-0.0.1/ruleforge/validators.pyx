import re

cdef class Validator:
    cpdef bint validate(self, object element):
        raise NotImplementedError

cdef class TypeValidator(Validator):
    cdef object expected_type
    def __cinit__(self, object expected_type):
        self.expected_type = expected_type

    cpdef bint validate(self, object element):
        return isinstance(element, self.expected_type)

cdef class NullValidator(Validator):
    cdef bint nullable
    def __cinit__(self, bint nullable):
        self.nullable = nullable

    cpdef bint validate(self, object element):
        if element is None:
            return self.nullable
        return True

cdef class RegexValidator(Validator):
    cdef str pattern
    cdef bint full_match
    cdef bint negate
    cdef object engine

    def __cinit__(self, str pattern, bint full_match= True, bint negate= False, int flags = 0):
        self.pattern = pattern
        self.full_match = full_match
        self.negate = negate
        self.engine = re.compile(pattern, flags)

    cpdef bint validate(self, object element):
        if element is None:
            return True
        if not isinstance(element, str):
            return False
        if self.full_match:
            return bool(self.engine.fullmatch(element)) ^ self.negate
        return bool(self.engine.search(element)) ^ self.negate

cdef class ConstraintValidator(Validator):
    cdef str expr
    def __cinit__(self, str expr):
        self.expr = expr

    cpdef bint validate(self, object element):
        try:
            return bool(eval(self.expr, {"element": element}))
        except Exception:
            return False

cdef class CustomFunctionValidator(Validator):
    cdef object func
    def __cinit__(self, object func):
        self.func = func

    cpdef bint validate(self, element):
        return bool(self.func(element))

