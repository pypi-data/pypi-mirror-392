import inspect
import re
import time
import traceback
from pathlib import Path
from typing import Union, List, Tuple

from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from .types import GptDriverException


def delay(milliseconds: int) -> None:
    """
    Delays execution for a given number of milliseconds.

    Args:
        milliseconds (int): Number of milliseconds to delay execution.
    """
    time.sleep(milliseconds / 1000)


def get_api_key_from_capabilities(options: Union[AppiumOptions, List[AppiumOptions], None]) -> str:
    api_key = options.capabilities.get("gptdriver:apiKey") if options else None
    if not api_key:
        raise ValueError("Api key missing. Please provide it via 'gptdriver:apiKey' in capabilities")
    return api_key


def get_exception_body_map(command: str, exception: GptDriverException):
    cause_str = str(exception.__cause__)
    tb_list = traceback.format_exception(type(exception), exception, exception.__traceback__)
    stacktrace_str = ''.join(tb_list)

    body_map = {
        "timestamp": exception.timestamp,
        "stacktrace": str(exception.custom_stacktrace) or stacktrace_str,
        "message": cause_str,
        "class": type(exception.__cause__).__name__,
        "command": command
    }

    return body_map


def get_standard_locator(strategy: str) -> str:
    if strategy == "xpath":
        return By.XPATH
    elif strategy == "id":
        return By.ID
    elif strategy == "cssSelector":
        return By.CSS_SELECTOR
    elif strategy == "className":
        return By.CLASS_NAME
    elif strategy == "name":
        return By.NAME
    elif strategy == "linkText":
        return By.LINK_TEXT
    elif strategy == "partialLinkText":
        return By.PARTIAL_LINK_TEXT
    elif strategy == "tagName":
        return By.TAG_NAME
    else:
        raise ValueError(f"Unsupported locator strategy: {strategy}")


def get_appium_locator(strategy: str) -> str:
    if strategy == "xpath":
        return AppiumBy.XPATH
    elif strategy == "id":
        return AppiumBy.ID
    elif strategy == "cssSelector":
        return AppiumBy.CSS_SELECTOR
    elif strategy == "className":
        return AppiumBy.CLASS_NAME
    elif strategy == "name":
        return AppiumBy.NAME
    elif strategy == "linkText":
        return AppiumBy.LINK_TEXT
    elif strategy == "partialLinkText":
        return AppiumBy.PARTIAL_LINK_TEXT
    elif strategy == "tagName":
        return AppiumBy.TAG_NAME
    elif strategy == "accessibilityId":
        return AppiumBy.ACCESSIBILITY_ID
    elif strategy == "androidUIAutomator":
        return AppiumBy.ANDROID_UIAUTOMATOR
    elif strategy == "iosNsPredicateString":
        return AppiumBy.IOS_PREDICATE
    elif strategy == "iosClassChain":
        return AppiumBy.IOS_CLASS_CHAIN
    elif strategy == "custom":
        return AppiumBy.CUSTOM
    else:
        raise ValueError(f"Unsupported locator strategy: {strategy}")


def get_improved_locator(command: str) -> Tuple[str, str]:
    command = command.strip()

    pattern = r'By\.(\w+)\("(.+)"\)'
    appium_pattern = 'AppiumBy\.(\w+)\("(.+)"\)'

    matcher = re.search(pattern, command)
    appium_matcher = re.search(appium_pattern, command)

    if matcher:
        strategy = matcher.group(1)
        value = matcher.group(2)
        return get_standard_locator(strategy), value

    elif appium_matcher:
        strategy = appium_matcher.group(1)
        value = appium_matcher.group(2)
        return get_appium_locator(strategy), value

    raise ValueError(f"Invalid locator command: {command}")


def format_stacktrace(stacktrace: List[inspect.FrameInfo]) -> str:
    formatted_frames = []

    for frame_info in stacktrace:
        full_path = Path(frame_info.filename)
        func_name = frame_info.function
        line_no = frame_info.lineno
        file_name = full_path.name

        # Build module path from full path
        module_parts = full_path.parent.parts
        # Remove any empty root parts
        module_parts = [p for p in module_parts if p]
        # Replace invalid regex chars (like '-' or spaces) with '_' for safety
        module_parts = [p.replace('-', '_').replace(' ', '_') for p in module_parts]

        # Format: ModulePath.Function(FileName:LineNumber)
        formatted_frame = f"{module_parts[-1]}.{func_name}({file_name}:{line_no})"
        formatted_frames.append(formatted_frame)

    return str(formatted_frames)
