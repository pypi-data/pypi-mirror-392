=========
Changelog
=========

-------------------
v1.2.1 (2025-11-14)
-------------------

* Performance improvements
  * Use dictionary dispatch for encoder selection (O(1) vs O(n))
  * Cache encoder functions to avoid recreation
  * Add ``__slots__`` to frequently instantiated classes
* Code quality improvements
  * Add comprehensive type hints
  * Extract magic numbers to named constants
  * Use namedtuple for multi-value returns
  * Remove duplicate encoder creation

-------------------
v1.2.0 (2023-08-08)
-------------------

* Optimize bit shift
* Add pre-defined char sets
  * Base16 (RFC6468). Note: Same as HexUpper
  * Crockford32
  * WordSafe32 (Another avoid words strategy)

-------------------
v1.1.0 (2022-08-04)
-------------------

* Fixed bit shift selection error
* Reordered Puid constructor arguments
* Altered predefined characters order to match other PUID implementations
* Added cross-repo data testing
* Added optional histogram tests
* Update README
* Create test helpers

-------------------
v1.0.0 (2022-07-29)
-------------------

Initial Release
