# GraphReasoning package initialization with error handling
import warnings

warnings.filterwarnings("ignore")

# Try to import each module with error handling
available_modules = []
failed_modules = []

try:
    from GraphReasoning.utils import *
    available_modules.append('utils')
except ImportError as e:
    failed_modules.append(('utils', str(e)))

try:
    from GraphReasoning.graph_tools import *
    available_modules.append('graph_tools')
except ImportError as e:
    failed_modules.append(('graph_tools', str(e)))

try:
    from GraphReasoning.graph_analysis import *
    available_modules.append('graph_analysis')
except ImportError as e:
    failed_modules.append(('graph_analysis', str(e)))

try:
    from GraphReasoning.graph_generation import *
    available_modules.append('graph_generation')
except ImportError as e:
    failed_modules.append(('graph_generation', str(e)))

try:
    from GraphReasoning.agents import *
    available_modules.append('agents')
except ImportError as e:
    failed_modules.append(('agents', str(e)))

try:
    from GraphReasoning.openai_tools import *
    available_modules.append('openai_tools')
except ImportError as e:
    failed_modules.append(('openai_tools', str(e)))
    # OpenAI is optional, so we don't raise an error

# Print status if there are any failures
if failed_modules and __name__ != "__main__":
    import sys
    if not getattr(sys, '_graphreasoning_warning_shown', False):
        sys._graphreasoning_warning_shown = True
        print(f"GraphReasoning: Some modules could not be loaded due to missing dependencies.")
        print(f"Available modules: {', '.join(available_modules)}")
        print(f"To enable all features, install: pip install openai transformers guidance-ai torch")

