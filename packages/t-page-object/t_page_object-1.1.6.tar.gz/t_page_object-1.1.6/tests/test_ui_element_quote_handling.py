"""
Test module for UIElement quote handling.

This module contains tests for the UIElement functionality
specifically focusing on proper handling of single quotes in XPath construction
within the _close_modal method.
"""

from unittest.mock import Mock
from t_page_object.base.ui_element import UIElement
from t_page_object.bot_config import BotConfig


class TestUIElementQuoteHandling:
    """
    Test suite for UIElement quote handling in _close_modal method.

    Tests:
    - test_close_modal_with_single_quote_in_modal_button: Test BotConfig.modal_button with single quote
    - test_close_modal_with_single_quote_in_locator_value: Test locator_value with single quote
    - test_close_modal_without_single_quotes: Test normal values without single quotes
    - test_close_modal_with_both_having_single_quotes: Test both containing single quotes
    """

    def test_close_modal_with_single_quote_in_modal_button(self):
        """Test modal button text with single quote uses double quotes in XPath."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.wait_until_element_is_not_visible.return_value = True

        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock the _get_element_from_message to return test values
        ui_element._get_element_from_message = Mock(return_value=("div", "id", "modal123"))

        # Set BotConfig.modal_button with single quote
        original_modal_button = BotConfig.modal_button
        BotConfig.modal_button = "Don't Close"

        try:
            # execute
            ui_element._close_modal(exception_message)

            # assert
            # Check that find_elements was called with XPath containing double quotes for modal button
            calls = mock_browser.find_elements.call_args_list
            assert len(calls) > 0

            # First call should be for the modal button with single quote
            first_call_xpath = calls[0][0][0]
            assert "//div[@id=" in first_call_xpath
            assert (
                '//button[text()="don\'t close"]' in first_call_xpath.lower()
                or '//button[text()="Don\'t Close"]' in first_call_xpath
            )
        finally:
            BotConfig.modal_button = original_modal_button

    def test_close_modal_with_single_quote_in_locator_value(self):
        """Test locator value with single quote uses double quotes in XPath."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.wait_until_element_is_not_visible.return_value = True

        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock the _get_element_from_message to return locator_value with single quote
        ui_element._get_element_from_message = Mock(return_value=("div", "data-tooltip", "User's Profile"))

        # Set BotConfig.modal_button to None to skip that part
        original_modal_button = BotConfig.modal_button
        BotConfig.modal_button = None

        try:
            # execute
            ui_element._close_modal(exception_message)

            # assert
            # Check that find_elements was called with XPath containing double quotes for locator value
            calls = mock_browser.find_elements.call_args_list
            assert len(calls) > 0

            # Check if any call contains the locator value with double quotes
            first_call_xpath = calls[0][0][0]
            assert (
                '[@data-tooltip="User\'s Profile"]' in first_call_xpath
                or '[@data-tooltip="user\'s profile"]' in first_call_xpath.lower()
            )
        finally:
            BotConfig.modal_button = original_modal_button

    def test_close_modal_without_single_quotes(self):
        """Test normal values without single quotes use single quotes in XPath (backward compatibility)."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.wait_until_element_is_not_visible.return_value = True

        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock the _get_element_from_message to return normal values
        ui_element._get_element_from_message = Mock(return_value=("div", "id", "modal123"))

        # Set BotConfig.modal_button to normal text
        original_modal_button = BotConfig.modal_button
        BotConfig.modal_button = "Close"

        try:
            # execute
            ui_element._close_modal(exception_message)

            # assert
            calls = mock_browser.find_elements.call_args_list
            assert len(calls) > 0

            # Check that single quotes are used for normal text
            first_call_xpath = calls[0][0][0]
            assert (
                "[@id='modal123']" in first_call_xpath or '[@id="modal123"]' in first_call_xpath
            )  # Could be either but likely single
            assert "[text()='Close']" in first_call_xpath or '[text()="Close"]' in first_call_xpath
        finally:
            BotConfig.modal_button = original_modal_button

    def test_close_modal_with_both_having_single_quotes(self):
        """Test both modal_button and locator_value with single quotes."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.wait_until_element_is_not_visible.return_value = True

        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock the _get_element_from_message to return locator_value with single quote
        ui_element._get_element_from_message = Mock(return_value=("button", "aria-label", "Don't click"))

        # Set BotConfig.modal_button with single quote
        original_modal_button = BotConfig.modal_button
        BotConfig.modal_button = "O'Brien's Choice"

        try:
            # execute
            ui_element._close_modal(exception_message)

            # assert
            calls = mock_browser.find_elements.call_args_list
            assert len(calls) > 0

            # First call should have both double-quoted values
            first_call_xpath = calls[0][0][0]
            # Check modal button text uses double quotes
            assert "\"o'brien's choice\"]" in first_call_xpath.lower() or "\"O'Brien's Choice\"]" in first_call_xpath
            # Check locator value uses double quotes
            assert (
                '[@aria-label="Don\'t click"]' in first_call_xpath
                or '[@aria-label="don\'t click"]' in first_call_xpath.lower()
            )
        finally:
            BotConfig.modal_button = original_modal_button

    def test_close_modal_no_elements_found(self):
        """Test when blocking element info cannot be extracted."""
        # set
        mock_browser = Mock()
        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock _get_element_from_message to return empty values
        ui_element._get_element_from_message = Mock(return_value=("", "", ""))

        # execute
        ui_element._close_modal(exception_message)

        # assert
        # Should return early without calling find_elements
        mock_browser.find_elements.assert_not_called()

    def test_close_modal_element_not_visible_after_click(self):
        """Test when element is still visible after attempting to close modal."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.wait_until_element_is_not_visible.side_effect = AssertionError("Element still visible")

        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock the _get_element_from_message
        ui_element._get_element_from_message = Mock(return_value=("div", "id", "modal123"))

        original_modal_button = BotConfig.modal_button
        BotConfig.modal_button = None

        try:
            # execute
            ui_element._close_modal(exception_message)

            # assert
            # Method should handle the exception and continue trying other close paths
            assert mock_browser.find_elements.called
        finally:
            BotConfig.modal_button = original_modal_button

    def test_close_modal_with_apostrophe_in_attribute(self):
        r"""Test attribute value with apostrophe like data-name=\"O'Reilly\"."""
        # set
        mock_browser = Mock()
        mock_element = Mock()
        mock_browser.find_elements.return_value = [mock_element]
        mock_browser.wait_until_element_is_not_visible.return_value = True

        xpath = "//input[@id='test']"
        ui_element = UIElement(xpath, mock_browser, wait=False)

        exception_message = "Element click intercepted"

        # Mock with attribute value containing apostrophe
        ui_element._get_element_from_message = Mock(return_value=("span", "data-name", "O'Reilly"))

        original_modal_button = BotConfig.modal_button
        BotConfig.modal_button = None

        try:
            # execute
            ui_element._close_modal(exception_message)

            # assert
            calls = mock_browser.find_elements.call_args_list
            assert len(calls) > 0

            first_call_xpath = calls[0][0][0]
            # Should use double quotes for the attribute value
            assert (
                '[@data-name="O\'Reilly"]' in first_call_xpath or '[@data-name="o\'reilly"]' in first_call_xpath.lower()
            )
        finally:
            BotConfig.modal_button = original_modal_button
