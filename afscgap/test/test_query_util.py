import unittest

import afscgap.query_util


class QueryUtilTests(unittest.TestCase):

    def test_ords_none(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': None})
        self.assertIsNone(result['test'])

    def test_ords_str(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': 'a'})
        self.assertEquals(result['test'], 'a')

    def test_ords_float(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': 1.23})
        self.assertAlmostEquals(result['test'], 1.23)

    def test_ords_int(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': 123})
        self.assertAlmostEquals(result['test'], 123)

    def test_ords_dict(self):
        result = afscgap.query_util.interpret_query_to_ords({
            'test': {'a': 1, 'b': '2'}
        })
        self.assertEquals(result['test']['a'], 1)
        self.assertEquals(result['test']['b'], '2')

    def test_ords_limit_lower_bound(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': (1, None)})
        self.assertEquals(result['test']['$gte'], 1)

    def test_ords_limit_upper_bound(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': (None, 1)})
        self.assertEquals(result['test']['$lte'], 1)

    def test_ords_limit_range(self):
        result = afscgap.query_util.interpret_query_to_ords({'test': (1, 2)})
        self.assertEquals(result['test']['$between'][0], 1)
        self.assertEquals(result['test']['$between'][1], 2)

    def test_py_none(self):
        result = afscgap.query_util.interpret_query_to_py({'test': None})
        self.assertIsNone(result['test'])

    def test_py_str(self):
        result = afscgap.query_util.interpret_query_to_py({'test': 'a'})
        self.assertTrue(result['test']('a'))
        self.assertFalse(result['test']('b'))

    def test_py_float(self):
        result = afscgap.query_util.interpret_query_to_py({'test': 1.23})
        self.assertTrue(result['test'](1.23))
        self.assertFalse(result['test'](1.24))

    def test_py_int(self):
        result = afscgap.query_util.interpret_query_to_py({'test': 123})
        self.assertTrue(result['test'](123))
        self.assertFalse(result['test'](124))

    def test_py_dict(self):
        with self.assertRaises(RuntimeError):
            afscgap.query_util.interpret_query_to_py({
                'test': {'a': 1, 'b': '2'}
            })

    def test_py_limit_lower_bound(self):
        result = afscgap.query_util.interpret_query_to_py({'test': (1, None)})
        self.assertTrue(result['test'](123))
        self.assertFalse(result['test'](0))

    def test_py_limit_upper_bound(self):
        result = afscgap.query_util.interpret_query_to_py({'test': (None, 1)})
        self.assertTrue(result['test'](0))
        self.assertFalse(result['test'](2))

    def test_py_limit_range(self):
        result = afscgap.query_util.interpret_query_to_py({'test': (1, 2)})
        self.assertTrue(result['test'](1.5))
        self.assertFalse(result['test'](3))
