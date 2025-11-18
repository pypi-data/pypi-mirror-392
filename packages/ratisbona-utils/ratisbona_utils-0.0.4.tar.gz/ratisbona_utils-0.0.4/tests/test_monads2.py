import unittest
from multiprocessing.pool import ExceptionWithTraceback

from ratisbona_utils.monads import Maybe, Just, Nothing, Error, UnexpectedNothingError


class TestMaybe(unittest.TestCase):

    def test_just_must_be_just(self):
        self.assertTrue(Just(10).is_just)

    def test_just_must_not_be_nothing(self):
        self.assertFalse(Just(10).is_nothing)

    def test_just_must_not_be_error(self):
        self.assertFalse(Just(10).is_error)

    def test_just_must_unwrap_value(self):
        self.assertEqual(Just(10).unwrap_value(), 10)

    def test_just_must_raise_value_error_for_none(self):
        with self.assertRaises(ValueError):
            Just(None)

    def test_just_must_raise_value_error_for_error(self):
        with self.assertRaises(ValueError):
            Just(ValueError("An error occurred"))

    def test_just_must_not_unwrap_error(self):
        with self.assertRaises(ValueError):
            Just(10).unwrap_error()

    def test_just_must_be_true(self):
        self.assertTrue(Just(10))

    def test_just_or_error_must_be_just(self):
        self.assertTrue(Just(10) | Error(ValueError("An error occurred")).is_just)

    def test_just_or_just_must_be_same_just(self):
        self.assertEqual(10, (Just(10) | Just(20)).unwrap_value())

    def test_just_or_nothing_must_be_same_just(self):
        self.assertEqual(10, (Just(10) | Nothing).unwrap_value())

    def test_just_of_just_must_just_be_just(self):
        self.assertTrue(10, Just(Just(10)).unwrap_value())

    def test_just_must_be_same_as_value(self):
        self.assertEqual(Just(10), 10)

    def test_just_must_be_same_as_other_just_if_value_is_equal(self):
        self.assertEqual(Just(10), Just(5 + 5))

    def test_just_must_be_same_as_maybe_value(self):
        self.assertEqual(Just(10), Maybe(10))

    def test_error_must_be_error(self):
        self.assertTrue(Error(ValueError("An error occurred")).is_error)

    def test_error_must_not_be_just(self):
        self.assertFalse(Error(ValueError("An error occurred")).is_just)

    def test_error_must_not_be_nothing(self):
        self.assertFalse(Error(ValueError("An error occurred")).is_nothing)

    def test_error_must_unwrap_error(self):
        self.assertEqual(
            "An test error occurred",
            Error(ValueError("An test error occurred")).unwrap_error().args[0],
        )

    def test_error_must_raise_value_error_for_just_value(self):
        with self.assertRaises(ValueError) as ve:
            Error(42)

    def test_error_must_raise_value_error_for_none(self):
        with self.assertRaises(ValueError) as ve:
            Error(None)

    def test_error_must_not_unwrap_value(self):
        with self.assertRaises(ValueError):
            Error(ValueError("An error occurred")).unwrap_value()

    def test_error_must_not_be_true(self):
        self.assertFalse(Error(ValueError("An error occurred")))

    def test_error_or_error_must_be_second_error(self):
        self.assertEqual(
            "Another error occurred",
            Error(ValueError("An error occurred"))
            | Error(ValueError("Another error occurred")).unwrap_error().args[0],
        )

    def test_error_or_just_must_be_just(self):
        self.assertTrue((Error(ValueError("An error occurred")) | Just(10)).is_just)

    def test_error_or_nothing_must_be_nothing(self):
        self.assertTrue((Error(ValueError("An error occurred")) | Nothing).is_nothing)

    def test_error_of_error_must_be_error(self):
        self.assertTrue(
            "An test error occurred",
            Error(Error(Error(ValueError("An test error occurred"))))
            .unwrap_error()
            .args[0],
        )

    def test_error_must_be_same_as_value(self):
        error = ValueError("A test error occurred")
        self.assertEqual(Error(error), error)

    def test_error_must_be_same_as_other_error_if_exceptions_are_equal(self):
        error = ValueError("A test error occurred")
        self.assertEqual(Error(error), Error(error))

    def test_error_must_be_same_as_maybe_error(self):
        error = ValueError("A test error occurred")
        self.assertEqual(Error(error), Maybe(error))

    def test_nothing_must_be_nothing(self):
        self.assertTrue(Nothing.is_nothing)

    def test_nothing_must_not_be_just(self):
        self.assertFalse(Nothing.is_just)

    def test_nothing_must_not_be_error(self):
        self.assertFalse(Nothing.is_error)

    def test_nothing_must_not_unwrap_value(self):
        with self.assertRaises(ValueError):
            Nothing.unwrap_value()

    def test_nothing_must_not_unwrap_error(self):
        with self.assertRaises(ValueError):
            Nothing.unwrap_error()

    def test_nothing_must_not_be_true(self):
        self.assertFalse(Nothing)

    def test_nothing_or_error_must_be_error(self):
        self.assertTrue((Nothing | Error(ValueError("An error occurred"))).is_error)

    def test_nothing_or_just_must_be_just(self):
        self.assertTrue((Nothing | Just(10)).is_just)

    def test_nothing_or_nothing_must_be_nothing(self):
        self.assertTrue((Nothing | Nothing).is_nothing)

    def test_nothing_must_equal_None(self):
        self.assertEqual(Nothing, None)

    def test_nothing_must_equal_other_nothing(self):
        self.assertEqual(Nothing, Nothing)

    def test_nothing_must_equal_maybe_none(self):
        self.assertEqual(Nothing, Maybe(None))

    def test_bind_to_just_must_apply_function(self):
        self.assertEqual(Just(10).bind(lambda x: x + 5).unwrap_value(), 15)

    def test_bind_to_nothing_must_return_nothing(self):
        self.assertTrue(Nothing.bind(lambda x: x + 5).is_nothing)

    def test_bind_to_error_must_return_error(self):
        self.assertTrue(
            Error(ValueError("An error occurred")).bind(lambda x: x + 5).is_error
        )

    def test_bind_to_just_of_function_raising_error_must_return_error(self):
        maybe_result = Just(10).bind(lambda x: x / 0)
        self.assertTrue(maybe_result.is_error)
        the_error = maybe_result.unwrap_error()
        self.assertIsInstance(the_error, ZeroDivisionError)
        self.assertTrue("Traceback" in the_error.__notes__[0])


    def test_binding_just_function_to_just_must_apply_function(self):
        def divide_by_2(x):
            return x / 2

        maybe_divide_by_2 = Just(divide_by_2)

        self.assertEqual(Just(10).bind(maybe_divide_by_2).unwrap_value(), 5)

    def test_binding_nothing_function_to_just_must_return_nothing(self):
        self.assertTrue(Just(10).bind(Nothing).is_nothing)

    def test_binding_error_function_to_just_must_return_error(self):
        error_function = Error(ValueError("An error occurred"))
        self.assertTrue(Just(10).bind(error_function).is_error)

    def test_binding_must_accept_additional_arguments(self):
        def add(x, y):
            return x + y

        self.assertEqual(Just(10).bind(add, 5).unwrap_value(), 15)

    def test_binding_additional_maybe_must_unwrap(self):
        def add(x, y):
            return x + y

        self.assertEqual(Just(10).bind(add, Just(5)).unwrap_value(), 15)

    def test_binding_additional_nothing_must_return_nothing(self):
        def add(x, y):
            return x + y

        self.assertTrue(Just(10).bind(add, Nothing).is_nothing)

    def test_binding_additional_error_must_return_error(self):
        def add(x, y):
            return x + y

        self.assertTrue(
            Just(10).bind(add, Error(ValueError("An error occurred"))).is_error
        )

    def test_in_binding_errors_of_original_monad_must_be_dominant(self):
        originally_in_error = Error(ValueError("The original error"))
        originally_nothing = Nothing

        erratic_function = Error(ValueError("Erratic function error"))
        erratic_argument = Error(ValueError("Erratic argument error"))

        self.assertEqual(
            "The original error",
            originally_in_error.bind(erratic_function).unwrap_error().args[0],
        )
        self.assertEqual(
            "The original error",
            originally_in_error.bind(lambda x: x, erratic_argument)
            .unwrap_error()
            .args[0],
        )
        self.assertTrue(originally_nothing.bind(erratic_function).is_nothing)
        self.assertTrue(
            originally_nothing.bind(lambda x: x, erratic_argument).is_nothing
        )

    def test_maybe_recover_must_recover_on_just_returnvalue(self):
        error_value = Error(ValueError("An error occurred"))
        result = error_value.maybe_recover(lambda e: 20)
        self.assertTrue(result.is_just)
        self.assertFalse(result.is_error)
        self.assertFalse(result.is_nothing)
        self.assertEqual(result.unwrap_value(), 20)

    def test_maybe_recover_must_not_recover_on_error_returnvalue(self):
        error_value = Error(ValueError("An error occurred"))
        result = error_value.maybe_recover(lambda e: Error(ValueError("Another error")))
        self.assertTrue(result.is_error)
        self.assertFalse(result.is_just)
        self.assertFalse(result.is_nothing)
        self.assertEqual(result.unwrap_error().args[0], "An error occurred")

    def test_maybe_recover_must_recover_on_nothing_returnvalue(self):
        error_value = Error(ValueError("An error occurred"))
        result = error_value.maybe_recover(lambda e: Nothing)
        self.assertTrue(result.is_nothing)

    def test_default_or_throw_must_return_value(self):
        self.assertEqual(10, Just(10).default_or_throw(20))

    def test_default_or_throw_must_raise_error(self):
        with self.assertRaises(ValueError):
            Error(ValueError("An error occurred")).default_or_throw(20)

    def test_default_or_throw_must_substitute_default_on_nothing(self):
        self.assertEqual(20, Nothing.default_or_throw(20))

    def test_default_on_error_must_return_value(self):
        self.assertEqual(10, Just(10).default_also_on_error(20))

    def test_default_on_error_must_return_default_on_error(self):
        self.assertEqual(20, Error(ValueError("An error occurred")).default_also_on_error(20))

    def test_default_on_error_must_return_default_on_nothing(self):
        self.assertEqual(20, Nothing.default_also_on_error(20))

    def test_value_or_throw_must_return_value(self):
        self.assertEqual(10, Just(10).value_or_throw())

    def test_value_or_throw_must_raise_error_on_error(self):
        with self.assertRaises(ValueError):
            Error(ValueError("An error occurred")).value_or_throw()

    def test_value_or_throw_must_raise_error_on_nothing(self):
        with self.assertRaises(UnexpectedNothingError) as une:
            Nothing.value_or_throw()
        note = une.exception.__notes__[0]
        print(note)
        self.assertTrue("Traceback" in note)

    def test_getitem_must_return_value(self):
        maybe_dict = Just({"a": 10, "b": 20})
        maybe_a = maybe_dict.__getitem__("a")
        a_value = maybe_a.unwrap_value()
        self.assertEqual(10, a_value)

        self.assertEqual(10, maybe_dict["a"].unwrap_value())

    def test_iterating_over_maybe_of_iterable_must_result_in_maybe_items(self):
        maybe_list = Just([1, 2, 3])
        for item, expected in zip(maybe_list, [1,2,3]):
            self.assertIsInstance(item, Maybe)
            self.assertTrue(item.is_just)
            self.assertEqual(expected, item.unwrap_value())

    def test_iterating_over_nothing_must_not_iterate(self):
        for _ in Nothing:
            self.fail("Nothing should not iterate")

    def test_iterating_over_error_must_not_iterate(self):
        for _ in Error(ValueError("An error")):
            self.fail("Error should not iterate")

    def test_iterating_over_single_element_should_iterate_exactly_once(self):
        for item in Just(10):
            self.assertEqual(10, item.unwrap_value())

    def test_in_must_return_true_if_item_in_monads_value(self):
        self.assertTrue(10 in Just([9,10,11]))
        self.assertTrue("a" in Just({"a": 10, "b": 20}))

    def test_in_must_return_false_if_item_not_in_monads_value(self):
        self.assertFalse(10 in Just([9,11]))
        self.assertFalse("a" in Just({"b": 10, "c": 20}))

    def test_in_must_return_true_if_value_of_item_in_monads_value(self):
        self.assertTrue(Just(10) in Just([9,10,11]))
        self.assertTrue(Just("a") in Just({"a": 10, "b": 20}))

    def test_in_must_be_false_for_nothing(self):
        self.assertFalse(10 in Nothing)
        self.assertFalse("a" in Nothing)

    def test_in_must_be_false_for_error(self):
        self.assertFalse(10 in Error(ValueError("An error")))
        self.assertFalse("a" in Error(ValueError("An error")))

    def test_in_must_be_false_for_nothing_item(self):
        self.assertFalse(Nothing in Just([9,10,11]))
        self.assertFalse(Nothing in Just({"a": 10, "b": 20}))

    def test_in_must_be_false_for_error_item(self):
        self.assertFalse(Error(ValueError("An error")) in Just([9,10,11]))
        self.assertFalse(Error(ValueError("An error")) in Just({"a": 10, "b": 20}))









if __name__ == "__main__":
    unittest.main()
