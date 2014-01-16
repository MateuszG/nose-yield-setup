import nose
from nose.case import (
    FunctionTestCase,
    try_run
)
from nose.loader import TestLoader
from nose.plugins import Plugin
from nose.pyversion import ismethod
from nose.util import (
    isclass,
    isgenerator
)


class NewFunctionTestCase(FunctionTestCase):
    """
    Rewrite part of class FunctionTestCase, to get same format of output
    test results for generators, like other tests of class.
    """

    def __init__(
            self, cls, test, test_name, setUp=None, tearDown=None, arg=tuple(),
            descriptor=None
    ):
        self.test_name = test_name
        self.cls = cls
        self.inst = self.cls()
        FunctionTestCase.__init__(self, test, setUp, tearDown, arg, descriptor)

    def setUp(self):
        """
        Run any setup function attached to the test function.
        Added setup_mocks which must be run when call mock from inherited class.
        """
        try_run(self.inst, ('setup_mocks', 'setUp'))

    def tearDown(self):
        """
        Added teardown_mocks which must be run to stop all mocks.
        """
        try_run(self.inst, ('teardown_mocks', 'tearDown'))

    def __str__(self):
        """
        Added self.test_name to display in output also "check_" part of test
        in full path to actual processing test.
        """
        func, _ = self._descriptors()
        name = func.__name__
        name = "%s.%s.%s.%s" % (
            self.cls.__module__,
            self.cls.__name__,
            self.test_name,
            name
        )
        return name
    __repr__ = __str__


class CustomLoaderForGenerators(TestLoader):
    """
    Based on nose function: loadTestsFromGenerator from loader.py,
    which Lazy-load tests from a generator function.
    """

    def load_tests_from_generator_method_with_set_up(self, generator, cls):
        """
        Create instance of TestCase to call setUp, which is need to
        prevent error: (No api proxy found for service "datastore_v3".
        """
        test_class_instance = cls()
        test_class_instance.setUp()

        def generate():
            """
            Rewrite internal function 'generate' from
            loadTestsFromGeneratorMethod to send 'test_name' of "check_"
            and limit operations to have only those which are required.
            """
            for test in generator(test_class_instance):
                test_func, arg = self.parseGeneratedTest(test)
                yield NewFunctionTestCase(
                    test=test_func,
                    arg=arg,
                    cls=cls,
                    test_name=generator.im_func.__name__
                )
        # Back to built-in nose method
        return self.suiteClass(generate, context=generator, can_split=False)


class YieldWithSetUp(Plugin):
    """
    Main plugin yield class definition. Features: Run setUp on generators
    and display full path in output during test.
    """
    name = 'yield'

    def __init__(self):
        super(YieldWithSetUp, self).__init__()

    def makeTest(self, obj, cls):
        """
        Only this function from nose API give test (cls) and testCase (cls).
        """
        if ismethod(obj) and isgenerator(obj) and isclass(cls):

            # If generator is found, override loader from nose
            x = CustomLoaderForGenerators()

            # 'return' is required on x because with yield tests in generator
            # will not change to next
            return x.load_tests_from_generator_method_with_set_up(obj, cls)

if __name__ == '__main__':
    nose.main()
