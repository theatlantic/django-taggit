__version_info__ = (0, 9, 2)
__atl_version_info__ = (2, 0, 5)
__version__ = '%s-atl-%s' % tuple(['.'.join(map(str, v))
                                   for v in [__version_info__, __atl_version_info__]])
