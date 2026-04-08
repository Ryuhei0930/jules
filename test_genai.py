import os
import sys
from unittest.mock import MagicMock
sys.modules['google.genai'] = MagicMock()
from google import genai

print("Mock loaded")
