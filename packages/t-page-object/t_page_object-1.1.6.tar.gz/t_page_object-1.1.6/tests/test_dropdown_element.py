"""
Test module for DropdownElement quote handling.

This module contains tests for the DropdownElement functionality
specifically focusing on proper handling of single quotes in XPath construction.
"""

from unittest.mock import Mock
from t_page_object.elements.dropdown_element import DropdownElement


class TestDropdownElementQuoteHandling:
    """
    Test suite for DropdownElement quote handling in click_and_select_option.

    Tests:
    - test_click_and_select_option_with_single_quote_exact: Test exact match with single quote
    - test_click_and_select_option_with_single_quote_contains: Test contains match with single quote
    - test_click_and_select_option_without_single_quote: Test normal text without single quotes
    - test_click_and_select_option_multiple_single_quotes: Test text with multiple single quotes
    """

    def test_click_and_select_option_with_single_quote_exact(self):
        """Test exact match with text containing single quote uses double quotes in XPath."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.get_webelement.return_value = mock_element

        xpath = "//select[@id='dropdown']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False)

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute
        result = dropdown.click_and_select_option("O'Brien", match_strategy="exact")

        # assert
        assert result is True
        dropdown.click_element_when_visible.assert_called_once()

        # Verify the XPath uses double quotes for text with single quote
        call_args = mock_browser.find_elements.call_args[0][0]
        assert '"o\'brien"' in call_args.lower()
        assert "translate(normalize-space(text())" in call_args

    def test_click_and_select_option_with_single_quote_contains(self):
        """Test contains match with text containing single quote uses double quotes in XPath."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.get_webelement.return_value = mock_element

        xpath = "//select[@id='dropdown']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False)

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute
        result = dropdown.click_and_select_option("O'Neill", match_strategy="contains")

        # assert
        assert result is True
        dropdown.click_element_when_visible.assert_called_once()

        # Verify the XPath uses double quotes for text with single quote
        call_args = mock_browser.find_elements.call_args[0][0]
        assert '"o\'neill"' in call_args.lower()
        assert "contains(" in call_args

    def test_click_and_select_option_without_single_quote(self):
        """Test normal text without single quotes uses single quotes in XPath (backward compatibility)."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.get_webelement.return_value = mock_element

        xpath = "//select[@id='dropdown']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False)

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute
        result = dropdown.click_and_select_option("Normal Text", match_strategy="exact")

        # assert
        assert result is True
        dropdown.click_element_when_visible.assert_called_once()

        # Verify the XPath uses single quotes for normal text
        call_args = mock_browser.find_elements.call_args[0][0]
        assert "'normal text'" in call_args.lower()
        assert '"normal text"' not in call_args.lower()

    def test_click_and_select_option_multiple_single_quotes(self):
        """Test text with multiple single quotes uses double quotes in XPath."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.get_webelement.return_value = mock_element

        xpath = "//ul[@class='options']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False)

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute
        result = dropdown.click_and_select_option("O'Neill's Choice", match_strategy="exact")

        # assert
        assert result is True
        dropdown.click_element_when_visible.assert_called_once()

        # Verify the XPath uses double quotes
        call_args = mock_browser.find_elements.call_args[0][0]
        assert "\"o'neill's choice\"" in call_args.lower()

    def test_click_and_select_option_not_found(self):
        """Test when option is not found in dropdown."""
        # set
        mock_browser = Mock()
        mock_browser.find_elements.return_value = []  # No elements found

        xpath = "//select[@id='dropdown']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False)

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute
        result = dropdown.click_and_select_option("Nonexistent", match_strategy="exact")

        # assert
        assert result is False
        dropdown.click_element_when_visible.assert_called_once()

    def test_click_and_select_option_custom_option_tag(self):
        """Test with custom option_tag parameter."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.get_webelement.return_value = mock_element

        xpath = "//div[@class='custom-dropdown']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False, option_tag="div")

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute
        result = dropdown.click_and_select_option("O'Brien", match_strategy="exact")

        # assert
        assert result is True

        # Verify the XPath uses the custom option tag
        call_args = mock_browser.find_elements.call_args[0][0]
        assert "//div" in call_args
        assert '"o\'brien"' in call_args.lower()

    def test_click_and_select_option_invalid_strategy(self):
        """Test with invalid match_strategy raises ValueError."""
        # set
        mock_browser = Mock()
        xpath = "//select[@id='dropdown']"
        dropdown = DropdownElement(xpath, mock_browser, wait=False)

        # Mock the click_element_when_visible method
        dropdown.click_element_when_visible = Mock()

        # execute & assert
        try:
            dropdown.click_and_select_option("test", match_strategy="invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid match_strategy" in str(e)
            assert "Must be 'exact' or 'contains'" in str(e)
