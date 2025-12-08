import time
from collections import defaultdict
from langchain_core.callbacks import BaseCallbackHandler

class LoggingCallback(BaseCallbackHandler):
    def __init__(self):
        self.metrics = defaultdict(lambda: {'n_calls':0,'total_time':0,'mean_time':0})
        self.logs = []
        self.sequence = []
        self.task_type = ''
        self.active_tools = {}

    def on_tool_start(self, tool, input_str, **kwargs):
        tool_name = tool.get("name")
        self.logs.append({'tool':tool_name,'input':input_str,'output':None,'duration':None}) #Must be refactored if tool parallelism is allowed
        self.active_tools[tool_name] = time.perf_counter()

    def on_tool_end(self, output, **kwargs):
        end_time = time.perf_counter()
        tool_name = getattr(output, "name")
        start_time = self.active_tools.pop(tool_name)
        duration = end_time - start_time
        tool_output = getattr(output,"content")
        self.logs[-1]['output'] = tool_output #Must be refactored if tool parallelism is allowed
        self.logs[-1]['duration'] = duration

    def on_llm_start(self,llm,prompts,**kwargs):
        tool_name = "llm"
        self.logs.append({'tool':tool_name,'input':prompts,'output':None,'duration':None})
        self.active_tools[tool_name] = time.perf_counter()

    def on_llm_end(self, output,**kwargs):
        end_time = time.perf_counter()
        tool_name="llm"
        start_time = self.active_tools.pop(tool_name)
        duration = end_time - start_time
        gen = getattr(output,'generations')
        tool_output = getattr(gen[0][0],'text')
        self.logs[-1]['output'] = tool_output #Must be refactored if tool parallelism is allowed
        self.logs[-1]['duration'] = duration

    def on_chain_end(self, outputs, run_id=None, parent_run_id=None,**kwargs):
        if parent_run_id is not None:
            return
        for log in self.logs:
            tool_name = log['tool']
            self.sequence.append(tool_name)
            self.metrics[tool_name]['n_calls']+=1
            self.metrics[tool_name]['total_time']+=log['duration']
        
        for (tool,metrics) in self.metrics.items():
            self.metrics[tool]['mean_time'] = metrics['total_time']/metrics['n_calls']

        used_tools = list(filter(lambda a: a!='llm',self.sequence))
        if len(used_tools)>1:
            self.task_type='multitool'
        elif len(used_tools)==1:
            if used_tools[0] == 'get_context_information':
                self.task_type = 'question_answering'
            else:
                self.task_type = used_tools[0]
        else:
            self.task_type = 'generic_question'
