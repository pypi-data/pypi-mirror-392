from pathlib import Path
from typing import Any, Iterable, List, Optional, Callable

import concurrent.futures

from HowdenPipeline.manager.jsonMatcher import JsonMatcher
from HowdenPipeline.manager.tracker import Tracker
from HowdenPipeline.flow.parameter_serializer import ParameterSerializer
from HowdenPipeline.flow.pipeline_graph_manager import PipelineGraphManager
from HowdenPipeline.flow.step_namer import StepNamer
from HowdenPipeline.flow.step_hasher import StepHasher
from HowdenPipeline.flow.match import Match
from HowdenPipeline.flow.file_pipeline_runner import FilePipelineRunner

class GraphPipeline:
    def __init__(
            self,
            root_folder: str,
            tracker: Optional[Tracker] = None,
            delete_folder: bool = False,
            graph_manager: Optional[PipelineGraphManager] = None,
            serializer: Optional[ParameterSerializer] = None,
            hasher: Optional[StepHasher] = None,
            namer: Optional[StepNamer] = None,
            matcher_factory: Optional[Callable[[List[Match]], Any]] = None,
    ) -> None:
        """
        Initialize the pipeline responsible for executing a graph of processing steps on PDFs.

        Parameters
        ----------
        root_folder : str
            Path to the folder containing the PDF files to be processed. All PDFs
            discovered recursively within this folder are included in the pipeline run.

        tracker : Tracker, optional
            Optional tracking component used to record metrics, artifacts, and run
            information. When supplied, the pipeline reports its execution details
            through this tracker.

        delete_folder : bool
            Determines whether all step output folders should be removed before
            processing each file. When set to True, the pipeline forces a full
            recalculation of all steps rather than using any previously produced results.
        """

        self.delete_folder = delete_folder
        self.root_folder = Path(root_folder)
        self.file_paths_pdf: List[Path] = list(self.root_folder.rglob("*.pdf"))

        self.serializer = serializer or ParameterSerializer()
        self.hasher = hasher or StepHasher(self.serializer)
        self.namer = namer or StepNamer()

        self.graph_manager = graph_manager or PipelineGraphManager(
            hasher=self.hasher,
            namer=self.namer,
        )

        self.tracker = tracker
        if self.tracker:
            print("run mlflow by writing <mlflow ui> in cli")

        self.matcher_factory = matcher_factory or JsonMatcher
        self.matches: List[Match] = []

    def add_step(
            self,
            step: Any,
            dependencies: Optional[Iterable[Any]] = None,
            track: bool = False,
            filetype: Optional[str] = None,
            input_result: Optional[Any] = None
    ) -> None:
        self.graph_manager.add_step(
            step=step,
            dependencies=dependencies,
            track=track,
            filetype=filetype,
            input_result=input_result

        )

    def execute(self, workers: int = 4) -> List[Path]:
        if not self.file_paths_pdf:
            return []

        results: List[Path] = []

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = []
            for file_path in self.file_paths_pdf:
                graph_copy = self.graph_manager.graph.copy()
                runner = FilePipelineRunner(
                    graph=graph_copy,
                    serializer=self.serializer,
                    tracker=self.tracker,
                    match_holder=self.matches,
                    delete_folder = self.delete_folder
                )
                futures.append(
                    executor.submit(runner.run_for_file, file_path=file_path)
                )

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"Worker failed but pipeline continues: {exc}")
                    # You may log this instead:
                    # logger.error(f"Worker failed: {exc}")
                    continue

        if self.tracker and self.matcher_factory and self.matches:
            matcher = self.matcher_factory(self.matches)
            self.tracker.log_metrics(matcher.get_accuracy_per_filename())
            self.tracker.log_artifacts("././poetry.lock")

        return results
