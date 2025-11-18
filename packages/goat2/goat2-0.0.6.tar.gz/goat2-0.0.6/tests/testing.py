import os
import sys

package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, package_path)
import goat2 # type: ignore
from goat2 import print_source_code # type: ignore
from goat2.models import resnet18 # type: ignore
from goat2.utils import trainer # type: ignore
from goat2.simple import imgclass # type: ignore

print_source_code("gb")