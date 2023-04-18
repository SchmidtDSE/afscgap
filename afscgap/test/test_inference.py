import unittest
import unittest.mock

import afscgap.inference


class InferenceTests(unittest.TestCase):

    def setUp(self):
        self._api_result = afscgap.test.test_tools.make_result_json(
            'limited.json'
        )
        self._api_mock_requsetor = unittest.mock.MagicMock(
            return_value=self._api_result
        )
        self._api_cursor = afscgap.client.ApiServiceCursor(
            'BASE_URL',
            requestor=self._api_mock_requsetor
        )

        self._hauls_result = afscgap.test.test_tools.make_result_text(
            'hauls.csv'
        )
        self._hauls_mock_requsetor = unittest.mock.MagicMock(
            return_value=self._hauls_result
        )

        self._all_hauls_data = afscgap.inference.get_hauls_data(
            {},
            self._hauls_mock_requsetor
        )

        self._decorated_cursor = afscgap.inference.build_inference_cursor(
            {},
            self._api_cursor,
            requestor=self._hauls_mock_requsetor
        )

    def test_build_params_checker_rejects(self):
        checker = afscgap.inference.build_params_checker({'year': 2021})
        data_2021 = filter(lambda x: x.get_year() == 2021, self._all_hauls_data)
        example_2021 = list(data_2021)[0]
        self.assertTrue(checker(example_2021))


    def test_build_params_checker_accepts(self):
        checker = afscgap.inference.build_params_checker({'year': 2021})
        data_2021 = filter(lambda x: x.get_year() != 2021, self._all_hauls_data)
        example_2021 = list(data_2021)[0]
        self.assertFalse(checker(example_2021))

    def test_get_all_hauls(self):
        self.assertEquals(len(self._all_hauls_data), 3)
        
        years = set(map(lambda x: int(x.get_year()), self._all_hauls_data))
        self.assertEquals(len(years), 2)
        self.assertTrue(2021 in years)
        self.assertTrue(2000 in years)

    def test_filter_hauls(self):
        filtered_hauls = afscgap.inference.get_hauls_data(
            {'year': 2021},
            self._hauls_mock_requsetor
        )

        self.assertEquals(len(filtered_hauls), 2)

    def test_decorator_infer_pass_through(self):
        data_2021 = filter(lambda x: x.get_year() == 2021, self._all_hauls_data)
        example_2021 = list(data_2021)[0]
        decorated = afscgap.inference.ZeroCatchHaulDecorator(
            example_2021,
            'science',
            'fish',
            12,
            34,
            567
        )
        self.assertEquals(decorated.get_year(), 2021)

    def test_decorator_infer_override(self):
        data_2021 = filter(lambda x: x.get_year() == 2021, self._all_hauls_data)
        example_2021 = list(data_2021)[0]
        decorated = afscgap.inference.ZeroCatchHaulDecorator(
            example_2021,
            'science',
            'fish',
            12,
            34,
            567
        )
        self.assertEquals(decorated.get_cpue_weight_maybe(units='kg/ha'), 0)

    def test_decorator_infer_given(self):
        data_2021 = filter(lambda x: x.get_year() == 2021, self._all_hauls_data)
        example_2021 = list(data_2021)[0]
        decorated = afscgap.inference.ZeroCatchHaulDecorator(
            example_2021,
            'science',
            'fish',
            12,
            34,
            567
        )
        self.assertEquals(decorated.get_cpue_weight_maybe(units='kg/ha'), 0)

    def test_decorator_dict(self):
        data_2021 = filter(lambda x: x.get_year() == 2021, self._all_hauls_data)
        example_2021 = list(data_2021)[0]
        decorated = afscgap.inference.ZeroCatchHaulDecorator(
            example_2021,
            'science',
            'fish',
            12,
            34,
            567
        )
        decorated_dict = decorated.to_dict()
        self.assertEquals(decorated_dict['year'], 2021)

    def test_get_haul_key(self):
        example_api = list(self._api_cursor)[0]
        api_key = self._decorated_cursor._get_haul_key(example_api)

        match_hauls = filter(
            lambda x: int(x.get_haul()) == 215,
            self._all_hauls_data
        )
        example_haul = list(match_hauls)[0]
        haul_key = self._decorated_cursor._get_haul_key(example_haul)

        self.assertEqual(api_key, haul_key)

    def test_build_cursor_no_params(self):
        results = list(self._decorated_cursor)
        self.assertEqual(len(results), 6)

        haul_ids = set(map(lambda x: int(x.get_haul()), results))
        self.assertEqual(len(haul_ids), 3)
        self.assertTrue(110 in haul_ids)
        self.assertTrue(214 in haul_ids)
        self.assertTrue(215 in haul_ids)

    def test_build_cursor_params(self):
        decorated_cursor = afscgap.inference.build_inference_cursor(
            {'year': 2021},
            self._api_cursor,
            requestor=self._hauls_mock_requsetor
        )

        results = list(decorated_cursor)
        self.assertEqual(len(results), 4)

        haul_ids = set(map(lambda x: int(x.get_haul()), results))
        self.assertEqual(len(haul_ids), 2)
        self.assertTrue(214 in haul_ids)
        self.assertTrue(215 in haul_ids)
