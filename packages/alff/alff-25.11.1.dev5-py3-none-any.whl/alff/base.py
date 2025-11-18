import asyncio
from abc import ABC, abstractmethod
from pathlib import Path

from thkit.config import Config
from thkit.io import read_yaml
from thkit.jobman import ConfigRemoteMachines, alff_submit_job_multi_remotes
from thkit.markup import TextDecor
from thkit.path import filter_dirs

from alff.util.key import FILE_LOG_ALFF, FMT_STAGE
from alff.util.tool import alff_info_shorttext, init_alff_logger

logger = init_alff_logger()


#####ANCHOR Baseclass for workflow
class Workflow(ABC):
    """Base class for workflows.

    Workflow is the central part of ALFF. Each workflow contains list of stages to be executed.

    Subclass should reimplement:
        - `__init__()`: initialize the workflow, need to override these attributes:
            - self.stage_map
            - self.wf_name
        - `run()`: the main function to run the workflow. The default implementation is a loop over stages in `self.stage_map`, just for simple workflow. For complex workflow (e.g. with iteration like active learning), need to reimplement the `.run()` function.

    Example:
        ```python
        class WorkflowExample(Workflow):
            def __init__(self, params_file: str, machines_file: str):
                super().__init__(params_file, machines_file, SCHEMA_EXAMPLE)
                self.stage_map = {
                    "stage_name1": stage_function1,
                    "stage_name2": stage_function2,
                    "stage_name3": stage_function3,
                }
                self.wf_name = "Name of the workflow"
                return
        ```

    Notes:
        - `mdict` in this class is a single dictionary containing multiple remote machines, and will be parsed as `mdict_list` in `RemoteOperation` class.
    """

    def __init__(self, params_file: str, machines_file: str, schema_file: str = ""):
        self.params_file = params_file
        self.machines_file = machines_file
        self.schema_file = schema_file
        ### Machines config
        config_machine = ConfigRemoteMachines(self.machines_file)
        config_machine.check_connection()
        self.multi_mdicts = config_machine.multi_mdicts
        ### Params config
        self._validate_params_config()
        self.pdict = Config.loadconfig(self.params_file)
        self.stage_list = self._load_stage_list()

        ### Need to define in 'subclass.__init__()'
        self.stage_map = {}
        self.wf_name = "workflow_name"
        return

    def _load_stage_list(self):
        stage_list = self.pdict.get("stages", [])
        return stage_list

    def _validate_params_config(self):
        """Validate the params config file."""
        Config.validate(config_file=self.params_file, schema_file=self.schema_file)
        return

    def _update_config(self):
        pdict = self.pdict or {}
        multi_mdicts = self.multi_mdicts or {}
        pdict.update(Config.loadconfig(self.params_file))
        multi_mdicts.update(Config.loadconfig(self.machines_file))
        self.pdict = pdict
        self.multi_mdicts = multi_mdicts
        return

    def _print_intro(self):
        print(TextDecor(alff_info_shorttext()).mkcolor("blue"))
        logger.info(f"Start {self.wf_name}")
        logger.info(f"Logfile: {FILE_LOG_ALFF}")
        return

    def _print_outro(self):
        logger.info("FINISHED !")
        return

    def run(self):
        """The main function to run the workflow. This default implementation works for simple workflow,
        for more complex workflow (e.g. with iteration like active learning), need to reimplement this `.run()` function.
        """
        self._print_intro()
        stage_map = self.stage_map
        stage_list = self.stage_list
        ### main loop
        for i, (stage_name, stage_func) in enumerate(stage_map.items()):
            if stage_name in stage_list:
                logtext = f" stage_{i:{FMT_STAGE}}: {stage_name} "
                logger.info(TextDecor(logtext).fill_left(margin=20, length=52))
                stage_func(self.pdict, self.multi_mdicts)

        self._print_outro()
        return


#####ANCHOR Baseclass for remote operations
class RemoteOperation(ABC):
    """Base class for operations on remote machines.

    Each operation includes atleast 3 methods:
        - prepare
        - run
        - postprocess

    Subclass must reimplement these methods:
        - `__init__()`: initialize the operation, need to override these attributes:
        - `prepare()`: prepare all things needed for the run() method.
        - `postprocess()`: postprocess after the run() method.

    Notes:
        - Before using this class, must prepare file `work_dir/task_dirs.yml`
        - All paths (`work_dir`, `task_dirs`,...) are in POSIX format, and relative to `run_dir` (not `work_dir`).
        - All `abtractmethod` must be reimplemented in subclasses.
        - Do not change the `run()` method unless you know what you are doing.
    """

    def __init__(self, work_dir, pdict, multi_mdicts, mdict_prefix=""):
        ### Need to reimplement in subclass __init__()
        self.op_name = "Name of the operation"
        ## To filter already run structures
        self.has_files: list[str] = []
        self.no_files: list[str] = []

        ### Need to reimplement in subclass prepare()
        self.commandlist_list: list[list[str]] = []
        self.forward_files: list[str] = []
        self.backward_files: list[str] = []
        self.forward_common_files: list[str] = []
        self.backward_common_files: list[str] = []  # rarely used

        ### Do not change this part
        self.work_dir = work_dir
        self.pdict = pdict
        self.mdict_list = self._select_machines(multi_mdicts, mdict_prefix)
        self.task_dirs = self._load_task_dirs()
        return

    @abstractmethod
    def prepare(self):
        """Prepare all things needed for the `run()` method."""
        pass

    def run(self):
        """Function to submit jobs to remote machines.
        Note:
            - Orginal `taks_dirs` is relative to `run_dir`, and should not be changed. But the sumbmission function needs `taks_dirs` relative path to `work_dir`, so we make temporary change here.
        """
        logger.info(f"Run remote operation: '{self.op_name}'")

        task_dirs_need_run = self._filter_task_dirs()
        if len(task_dirs_need_run) == 0:
            logger.warning("No tasks found for remote jobs.")
            return
        else:
            logger.info(
                f"Select {len(task_dirs_need_run)}/{len(self.task_dirs)} tasks for remote run."
            )
        rel_task_dirs = [Path(p).relative_to(self.work_dir).as_posix() for p in task_dirs_need_run]

        ### Submit jobs
        asyncio.run(
            alff_submit_job_multi_remotes(
                mdict_list=self.mdict_list,
                commandlist_list=self.commandlist_list,
                work_dir=self.work_dir,
                task_dirs=rel_task_dirs,
                forward_files=self.forward_files,
                backward_files=self.backward_files,
                forward_common_files=self.forward_common_files,
                backward_common_files=self.forward_common_files,
                logger=logger,
            )
        )
        return

    @abstractmethod
    def postprocess(self):
        """Postprocess after the `run()` method."""
        pass

    def _load_task_dirs(self) -> list[str]:
        """Load task directories from `work_dir/task_dirs.yml`."""
        task_dirs_file = Path(self.work_dir) / "task_dirs.yml"
        if not task_dirs_file.exists():
            raise FileNotFoundError(f"File {task_dirs_file} not found. Please prepare it first.")
        task_dirs = read_yaml(task_dirs_file)
        return task_dirs

    def _select_machines(self, multi_mdicts: dict, mdict_prefix: str) -> list[dict]:
        ### Refer method `ConfigRemoteMachines.select_machines()`
        """Select machine dicts based on the prefix."""
        mdict_list = [v for k, v in multi_mdicts.items() if k.startswith(mdict_prefix)]
        if len(mdict_list) < 1:
            raise ValueError(f"No machine configs found with prefix: '{mdict_prefix}'")
        return mdict_list

    def _filter_task_dirs(self):
        """Function to filter already run structures."""
        task_dirs_need_run = filter_dirs(
            self.task_dirs,
            has_files=self.has_files,
            no_files=self.no_files,
        )
        return task_dirs_need_run


#####ANCHOR Support classes/functions
