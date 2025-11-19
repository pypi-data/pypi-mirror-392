# Python 3.14 Compatibility Issues

## Status: Not Currently Supported

As of November 2025, cheap-settings does **not** support Python 3.14 due to fundamental changes in how Python handles annotations.

## The Root Cause: PEP 649

Python 3.14 implements [PEP 649 - Deferred Evaluation of Annotations](https://peps.python.org/pep-0649/), which fundamentally changes how annotations work:

- **Before 3.14**: Annotations were evaluated at class definition time and stored in `__annotations__`
- **After 3.14**: Annotations are lazily evaluated via `__annotate_func__()` when accessed

## Specific Failures

### 1. Optional/Union Types Not Converting
```python
# Expected: Settings.timeout == 30 (int)
# Actual: Settings.timeout == '30' (str)
```
- Optional types return raw strings instead of converted values
- Affects: `Optional[int]`, `Optional[str]`, `Optional[datetime]`, etc.
- Test failures: All `test_optional_*` tests

### 2. Uninitialized Settings Not Recognized
```python
class Settings(CheapSettings):
    api_key: str  # No default value

# Expected: Settings.api_key returns None or raises
# Actual: AttributeError: no attribute 'api_key'
```
- Attributes with only type annotations (no defaults) aren't being detected
- The metaclass can't find these attributes during class creation
- Test failures: All `test_uninitialized_*` tests

### 3. New `__annotate_func__` Attribute
- Classes now have `__annotate_func__` instead of/in addition to `__annotations__`
- This appears in `dir()` output, breaking tests that check for specific attributes
- Test failure: `test_dir_includes_settings_and_methods`

### 4. `from_env()` Completely Broken
- Returns empty classes with no attributes
- Can't find any settings to extract from environment
- Test failures: All `test_from_env.py` tests

### 5. Command Line Argument Parsing Failures
- Boolean Optional types fail with `SystemExit: 2`
- Unable to handle `--debug true` style arguments
- Test failures: Multiple in `test_command_line.py`

### 6. Pickle Error Message Changed (Again)
- Error message for pickling local classes changed from "Can't get local object" to something else
- This is minor but indicates ongoing changes in Python internals
- Test failure: `test_local_class_pickle_limitation`

## Code Areas Affected

### `MetaCheapSettings.__new__()` (lines 197-285)
- Lines 210-232: Annotation collection from parent classes
- Lines 230-233: Processing current class annotations via `dct.pop("__annotations__", {})`
- Lines 258-264: Handling annotations without defaults

The core issue: `__annotations__` might not exist or might be empty even when annotations are present.

### `_convert_value_to_type()` (lines 91-185)
- Still being called but receiving wrong type information
- Optional/Union detection failing at lines 117-135

### `from_env()` method (lines 545-583)
- Line 567: `annotations = getattr(config_instance, "__annotations__", {})`
- Returns empty dict in Python 3.14

## Potential Solution Approaches

### 1. Check for `__annotate_func__`
```python
# In MetaCheapSettings.__new__
if hasattr(dct, '__annotate_func__'):
    # Python 3.14+ path
    annotate_func = dct['__annotate_func__']
    annotations = annotate_func(1)  # Format parameter: 1 = VALUE format
else:
    # Python 3.8-3.13 path
    annotations = dct.pop("__annotations__", {})
```

### 2. Update Annotation Collection
Need to handle both eager (3.13-) and lazy (3.14+) evaluation:
- Try `__annotate_func__()` first if it exists
- Fall back to `__annotations__`
- May need to force evaluation of annotations during metaclass creation

### 3. Fix `dir()` Implementation
- Filter out `__annotate_func__` from the attribute list
- Or document it as an expected attribute in 3.14+

## Test Output Summary

**Failed**: 33 tests
**Passed**: 125 tests
**Categories of failure**:
- Optional/Union type conversion: 12 tests
- Uninitialized settings: 9 tests
- from_env(): 7 tests
- Command line parsing: 4 tests
- Pickle: 1 test

## Why This Is Hard to Fix

1. **Fundamental change**: This isn't a bug fix, it's adapting to a new Python architecture
2. **Metaclass timing**: We build the config at class creation time, but annotations are now lazy
3. **Backward compatibility**: Need to support both old and new systems (3.8-3.13 vs 3.14+)
4. **Limited documentation**: PEP 649 is implemented but real-world migration guides are scarce

## Recommendation

1. **Short term**: Keep Python 3.14 in the "not supported" list
2. **Medium term**: Wait for the Python community to develop patterns for handling this
3. **Long term**: Implement dual-path support when patterns emerge

## References

- [PEP 649](https://peps.python.org/pep-0649/): The specification
- [Python 3.14 Release Notes](https://docs.python.org/3.14/whatsnew/3.14.html): Official changes
- Test failures: `.save/3-14-test-failures.txt`

## For Future Implementation

When ready to tackle this:
1. Set up a Python 3.14 development environment
2. Create a minimal test case for annotation handling
3. Implement `__annotate_func__` support in the metaclass
4. Test extensively with both 3.13 and 3.14
5. Consider if this warrants a major version bump (2.0.0)

---

*Note: This document created November 2025 based on test failures from GitHub Actions CI run.*
