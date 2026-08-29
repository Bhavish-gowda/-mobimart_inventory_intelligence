import io
import sys
from backend.engine.allocation.demo import run_demo

buffer = io.StringIO()
sys.stdout = buffer
run_demo()
sys.stdout = sys.__stdout__
print(buffer.getvalue()[:3000])
