# Copyright 2025 Subnoto
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Oak Python SDK for secure session management."""

__version__ = "0.1.0"

# Import client and server modules
# These are native extensions built from Rust via pyo3
try:
    from . import oak_client
except ImportError as e:
    # Provide a helpful error message
    import sys
    print(f"Failed to import oak_py_sdk.oak_client: {e}", file=sys.stderr)

    raise

# Server module is optional (not included in all distributions)
try:
    from . import oak_server
    __all__ = ["oak_client", "oak_server"]
except ImportError:
    __all__ = ["oak_client"]

