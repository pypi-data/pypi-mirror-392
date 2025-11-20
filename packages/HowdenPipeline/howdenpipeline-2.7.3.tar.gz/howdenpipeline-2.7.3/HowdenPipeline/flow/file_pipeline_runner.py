import json
from pathlib import Path
from typing import Any, List, Optional
import inspect
import asyncio
import shutil
import networkx as nx

from HowdenPipeline.manager.tracker import Tracker
from HowdenPipeline.flow.parameter_serializer import ParameterSerializer
from HowdenPipeline.flow.match import Match


class FilePipelineRunner:
    def __init__(
            self,
            graph: nx.DiGraph,
            serializer: Optional[ParameterSerializer] = None,
            tracker: Optional[Tracker] = None,
            match_holder: Optional[List[Match]] = None,
            delete_folder: bool = None,
    ) -> None:
        self.graph = graph
        self.serializer = serializer or ParameterSerializer()
        self.tracker = tracker
        self.match_holder = match_holder if match_holder is not None else []
        self.delete_folder = delete_folder

    def delete_folder_if_exists(self, path: Path) -> None:
        if self.delete_folder and path.exists() and path.is_dir():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _run_step_safe(step, input_data) -> Any:
        if inspect.iscoroutinefunction(step):
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(step(input_data))
            finally:
                loop.close()
                asyncio.set_event_loop(None)

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return step(input_data)
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------
    def run_for_file(self, file_path: Path) -> Path:
        print(f"Processing {file_path}")

        for node in self._traversal_order():
            step = self.graph.nodes[node]["cls"]
            dep_path = "/".join(self.graph.nodes[node]["full_path"])
            folder_path = Path(file_path.parent / dep_path)

            self.delete_folder_if_exists(folder_path)

            filetype = self.graph.nodes[node]["filetype"]
            result_file_path = folder_path / Path("result").with_suffix(f".{filetype}")

            if not result_file_path.exists():
                self._write_parameters(step, folder_path)
                input_data = self._build_input_data(node, file_path)
                hest = self.graph.nodes[node]["input_result"]
                if hest:
                    parts = folder_path.parts
                    idx = parts.index(hest[0])+1
                    new_path = Path(*parts[:idx])
                    print(new_path)
                    result = step(input_data, new_path / "result.md")
                else:
                    result = self._run_step_safe(step, input_data)

                result_file_path.write_text(result, encoding="utf-8")

            if self.graph.nodes[node]["track"]:
                path = file_path.parent
                match = Match(
                    result=result_file_path,
                    ground_truth=Path(f"{path}/GT_{step.name}.json"),
                )
                self.match_holder.append(match)

            self._propagate_result_path(node, result_file_path)

        return file_path

    def _traversal_order(self) -> List[str]:
        return list(nx.topological_sort(self.graph))

    def _write_parameters(self, step: Any, folder_path: Path) -> None:
        json_parameter = folder_path / "parameter.json"
        attrs = {
            k: v
            for k, v in step.__dict__.items()
            if not k.startswith("_") and k not in ("client", "provider")
        }
        serializable_attrs = self.serializer.make_serializable(attrs)
        json_parameter.write_text(
            json.dumps(
                serializable_attrs,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )

    def _build_input_data(self, node: str, file_path: Path) -> Any:
        dep_paths = [
            data["result_path_from_dep"]
            for _pred, _succ, data in self.graph.in_edges(node, data=True)
            if "result_path_from_dep" in data
        ]

        if dep_paths:
            dep_paths = [Path(p) for p in dep_paths]
            if len(dep_paths) == 1:
                return dep_paths[0]
            return dep_paths

        if isinstance(file_path, Path):
            return file_path
        return Path(file_path)

    def _propagate_result_path(self, node: str, result_file_path: Path) -> None:
        for _u, _v, data in self.graph.out_edges(node, data=True):
            data["result_path_from_dep"] = str(result_file_path)
