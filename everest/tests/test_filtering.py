"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 5, 2011.
"""

from everest.filtering import FilterSpecificationBuilder
from everest.specifications import FilterSpecificationFactory
from everest.specifications import ValueContainedFilterSpecification
from everest.specifications import ValueContainsFilterSpecification
from everest.specifications import ValueEndsWithFilterSpecification
from everest.specifications import ValueEqualToFilterSpecification
from everest.specifications import ValueGreaterThanFilterSpecification
from everest.specifications import ValueGreaterThanOrEqualToFilterSpecification
from everest.specifications import ValueInRangeFilterSpecification
from everest.specifications import ValueLessThanFilterSpecification
from everest.specifications import ValueLessThanOrEqualToFilterSpecification
from everest.specifications import ValueStartsWithFilterSpecification
from everest.testing import BaseTestCase

__docformat__ = 'reStructuredText en'
__all__ = ['ValueBoundFilterSpecificationBuilderTestCase',
           ]



class ValueBoundFilterSpecificationBuilderTestCase(BaseTestCase):
    builder = None

    def set_up(self):
        self.builder = FilterSpecificationBuilder(FilterSpecificationFactory())

    def tear_down(self):
        pass

    def test_build_equal_to(self):
        attr_name, attr_values = ('name', ['Nikos'])
        expected_spec = ValueEqualToFilterSpecification(attr_name, attr_values[0])
        self.builder.build_equal_to(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_not_equal_to(self):
        attr_name, attr_values = ('name', ['Nikos'])
        expected_spec = ValueEqualToFilterSpecification(attr_name, attr_values[0]).not_()
        self.builder.build_not_equal_to(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_starts_with(self):
        attr_name, attr_values = ('name', ['Ni'])
        expected_spec = ValueStartsWithFilterSpecification(attr_name, attr_values[0])
        self.builder.build_starts_with(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_not_starts_with(self):
        attr_name, attr_values = ('name', ['Ni'])
        expected_spec = ValueStartsWithFilterSpecification(attr_name, attr_values[0]).not_()
        self.builder.build_not_starts_with(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_ends_with(self):
        attr_name, attr_values = ('name', ['os'])
        expected_spec = ValueEndsWithFilterSpecification(attr_name, attr_values[0])
        self.builder.build_ends_with(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_not_ends_with(self):
        attr_name, attr_values = ('name', ['os'])
        expected_spec = ValueEndsWithFilterSpecification(attr_name, attr_values[0]).not_()
        self.builder.build_not_ends_with(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_contains(self):
        attr_name, attr_values = ('name', ['iko'])
        expected_spec = ValueContainsFilterSpecification(attr_name, attr_values[0])
        self.builder.build_contains(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_not_contains(self):
        attr_name, attr_values = ('name', ['iko'])
        expected_spec = ValueContainsFilterSpecification(attr_name, attr_values[0]).not_()
        self.builder.build_not_contains(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_less_than_or_equal_to(self):
        attr_name, attr_values = ('age', [34])
        expected_spec = ValueLessThanOrEqualToFilterSpecification(attr_name, attr_values[0])
        self.builder.build_less_than_or_equal_to(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_less_than(self):
        attr_name, attr_values = ('age', [34])
        expected_spec = ValueLessThanFilterSpecification(attr_name, attr_values[0])
        self.builder.build_less_than(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_greater_than_or_equal_to(self):
        attr_name, attr_values = ('age', [34])
        expected_spec = ValueGreaterThanOrEqualToFilterSpecification(attr_name, attr_values[0])
        self.builder.build_greater_than_or_equal_to(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_greater_than(self):
        attr_name, attr_values = ('age', [34])
        expected_spec = ValueGreaterThanFilterSpecification(attr_name, attr_values[0])
        self.builder.build_greater_than(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_in_range(self):
        attr_name, attr_values = ('age', [(30, 40)])
        expected_spec = ValueInRangeFilterSpecification(attr_name, *attr_values[0]) # pylint: disable=W0142
        self.builder.build_in_range(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_not_in_range(self):
        attr_name, attr_values = ('age', [(30, 40)])
        expected_spec = \
            ValueInRangeFilterSpecification(attr_name, *attr_values[0]).not_() # pylint: disable=W0142
        self.builder.build_not_in_range(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())


class CompositeFilterSpecificationBuilderTestCase(BaseTestCase):
    builder = None

    def set_up(self):
        self.builder = FilterSpecificationBuilder(FilterSpecificationFactory())

    def tear_down(self):
        pass

    def test_build_conjunction(self):
        left_name, left_values = ('age', [34])
        right_name, right_values = ('name', ['Nikos'])
        expected_spec = \
            ValueGreaterThanFilterSpecification(left_name, left_values[0]).and_(
            ValueEqualToFilterSpecification(right_name, right_values[0])
            )
        self.builder.build_greater_than(left_name, left_values)
        self.builder.build_equal_to(right_name, right_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_disjunction(self):
        attr_name, attr_values = ('name', ['Ni', 'Ol'])
        expected_spec = \
            ValueStartsWithFilterSpecification(attr_name, attr_values[0]).or_(
            ValueStartsWithFilterSpecification(attr_name, attr_values[1])
            )
        self.builder.build_starts_with(attr_name, attr_values)
        self.assert_equal(expected_spec, self.builder.get_specification())

    def test_build_conjunction_with_disjunction(self):
        left_name, left_values = ('age', [34, 44])
        right_name, right_values = ('name', ['Ni', 'Ol'])
        expected_spec = \
            ValueContainedFilterSpecification(left_name, left_values).and_(
                ValueStartsWithFilterSpecification(right_name, right_values[0]).or_(
                ValueStartsWithFilterSpecification(right_name, right_values[1])
                )
            )
        self.builder.build_equal_to(left_name, left_values)
        self.builder.build_starts_with(right_name, right_values)
        self.assert_equal(expected_spec, self.builder.get_specification())