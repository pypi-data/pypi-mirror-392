import sys, sysconfig
print(sys.implementation.cache_tag)        # should end with “t” (e.g. “cp314t”)
print(sysconfig.get_config_var("Py_GIL_DISABLED"))  # should be 1 for free-threaded
print(sys._is_gil_enabled())