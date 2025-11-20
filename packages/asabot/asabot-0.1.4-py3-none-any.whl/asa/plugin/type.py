from typing import Mapping, Any, Tuple, Union

PluginConfig = Mapping[str, Any]
PluginPath = str
PluginSpec = Union[PluginPath, Tuple[PluginPath, PluginConfig]]
