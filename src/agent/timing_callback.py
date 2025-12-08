import time
from collections import defaultdict
from langchain_core.callbacks import BaseCallbackHandler

class TimingCallback(BaseCallbackHandler):
    def __init__(self):
        self.tool_timings = defaultdict(lambda: {"calls": 0, "time": 0})
        self.active_tools = {}
        self.sequence=[]

    def on_tool_start(self, tool, input_str, **kwargs):
        tool_name = tool.get("name")
        self.sequence.append(tool_name)
        self.active_tools[tool_name] = time.perf_counter()

    def on_tool_end(self, tool, **kwargs):
        tool_name = getattr(tool, "name")
        start_time = self.active_tools.pop(tool_name)
        duration = time.perf_counter() - start_time
        self.tool_timings[tool_name]["calls"]+=1
        self.tool_timings[tool_name]["time"]+=duration
    
    def on_llm_start(self,llm,prompts,**kwargs):
        tool_name = "llm"
        self.sequence.append(tool_name)
        self.active_tools[tool_name] = time.perf_counter()

    def on_llm_end(self, resp,**kwargs):
        tool_name="llm"
        start_time = self.active_tools.pop(tool_name)
        duration = time.perf_counter()-start_time
        self.tool_timings[tool_name]["calls"]+=1
        self.tool_timings[tool_name]["time"]+=duration
