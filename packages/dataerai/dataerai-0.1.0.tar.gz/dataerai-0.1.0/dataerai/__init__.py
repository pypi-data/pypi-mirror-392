##
# @mainpage Portal Python Client Package
#
# @section Introduction
#
# This is the source-level documentation for the Portal Python Client package.
# For Portal command-line interface (CLI) documentation, please refer to the
# Portal wiki located on the Portal project page:
# https://github.com/ORNL/Portal/wiki
#
# @subsection Package Modules and Use Cases
#
# The Portal client Python packages consists of the Portal command-line client
# interface script (portal), a high-level programming interface module
# (CommandLib), a low-level message-oriented programming module (MessageLib), and
# two support modules (Connection and Config).
#
# The "portal" CLI, by default, supports human-interactive use, but it is also
# applicable to general scripting by utilizing the optional JSON output mode.
# For Python-specific scripting, the "CommandLib" module can be used to access
# the CLI-style text-based command interface, but with results returned directly
# as Python objects instead of JSON text. If greater control or features are
# needed, Python applications may use the "MessageLib" module to access the low-
# level message-oriented programming interface of Portal.
#
from . import VERSION

name = "dataerai"

version = VERSION.__version__
