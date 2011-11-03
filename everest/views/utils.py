"""
everest.views.utils

FOG Feb 4, 2011.
"""
from everest.mime import CSV_MIME

__docformat__ = 'reStructuredText en'

__author__ = 'F Oliver Gathmann'
__date__ = '$Date: 2011-02-04 14:51:06 +0100 (Fri, 04 Feb 2011) $'
__revision__ = '$Rev: 11783 $'
__source__ = '$URL::                                                          $'

__all__ = ['accept_csv_only',
           ]


def accept_csv_only(context, request): # pylint: disable-msg=W0613
    """
    This can be used as a custom predicate for view configurations with a
    CSV renderer that should only be invoked if this has been explicitly
    requested in the ACCEPT header by the client.
    """
    return CSV_MIME in request.accept.best_matches()