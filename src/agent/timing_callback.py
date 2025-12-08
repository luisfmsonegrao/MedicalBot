import time
from collections import defaultdict
from langchain_core.callbacks import BaseCallbackHandler

class MetadataCallback(BaseCallbackHandler):
    def __init__(self):
        self.metadata = defaultdict(lambda: [])
        self.active_tools = {}

    def on_tool_start(self, tool, input_str, **kwargs):
        tool_name = tool.get("name")
        self.metadata[tool_name].append({"input":input_str,"output":None,"duration":None}) #assumes no parallelism allowed
        self.active_tools[tool_name] = time.perf_counter()

    def on_tool_end(self, tool, **kwargs):
        end_time = time.perf_counter()
        tool_name = getattr(tool, "name")
        start_time = self.active_tools.pop(tool_name)
        duration = end_time - start_time
        tool_output = getattr(tool,"content")
        self.metadata[tool_name][-1]["output"] = tool_output #assumes no parallelism allowed
        self.metadata[tool_name][-1]["duration"] = duration

    def on_llm_start(self,llm,prompts,**kwargs):
        tool_name = "llm"
        self.metadata[tool_name].append({"input":prompts,"output":None,"duration":None}) #assumes no parallelism allowed
        self.active_tools[tool_name] = time.perf_counter()

    def on_llm_end(self, resp,**kwargs):
        print(resp)
        print(resp.__class__)
        end_time = time.perf_counter()
        tool_name="llm"
        start_time = self.active_tools.pop(tool_name)
        duration = end_time - start_time
        self.metadata[tool_name][-1]["duration"] = duration
        gen = getattr(resp,'generations')
        out = getattr(gen[0][0],'text')
        self.metadata[tool_name][-1]["output"] = out