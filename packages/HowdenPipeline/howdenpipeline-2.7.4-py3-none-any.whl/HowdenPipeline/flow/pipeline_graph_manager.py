from typing import Any, Iterable, Optional
import networkx as nx
from HowdenPipeline.flow.step_namer import StepNamer
from HowdenPipeline.flow.step_hasher import StepHasher


class PipelineGraphManager:
    def __init__(
            self,
            base_graph: Optional[nx.DiGraph] = None,
            hasher: Optional[StepHasher] = None,
            namer: Optional[StepNamer] = None,
    ) -> None:
        self.graph: nx.DiGraph = base_graph or nx.DiGraph()
        self._hasher = hasher or StepHasher()
        self._namer = namer or StepNamer()

    def add_step(
            self,
            step: Any,
            dependencies: Optional[Iterable[Any]] = None,
            track: bool = False,
            filetype: Optional[str] = None,
            input_result: Optional[str] = None,
    ) -> None:
        node_id = self._node_id_for(step)
        name = self._namer.name_for(step)
        node_hash = self._hasher.compute_hash(step)
        node_label = f"{name}_{node_hash}" if node_hash else name
        data_dependance = None
        if input_result:
            for h in input_result:
                dep_id2 = self._node_id_for(h)
                data_dependance = self.graph.nodes[dep_id2].get("full_path", [])

        if dependencies:
            for dep_step in dependencies:
                dep_id = self._node_id_for(dep_step)
                dep_path = self.graph.nodes[dep_id].get("full_path", [])
                full_path = dep_path + [node_label]

                self.graph.add_edge(dep_id, node_id)

                if node_id not in self.graph:
                    self.graph.add_node(node_id)

                self.graph.nodes[node_id].update(
                    cls=step,
                    name=name,
                    track=track,
                    filetype=filetype,
                    result=None,
                    hash=node_hash,
                    hash_path=[node_hash],
                    full_path=full_path,
                    input_result=data_dependance
                )
        else:
            self.graph.add_node(
                node_id,
                cls=step,
                name=name,
                track=track,
                filetype=filetype,
                result=None,
                hash=node_hash,
                hash_path=[node_hash],
                full_path=[node_label],
                input_result=data_dependance
            )

    @staticmethod
    def _node_id_for(step: Any) -> str:
        return hex(id(step))
