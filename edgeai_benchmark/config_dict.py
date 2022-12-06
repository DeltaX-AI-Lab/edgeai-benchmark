# Copyright (c) 2018-2021, Texas Instruments
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import yaml
from . import utils


class ConfigDict(dict):
    def __init__(self, input=None, **kwargs):
        super().__init__()
        # initialize with default values
        self._initialize()
        # read the given settings file
        input_dict = dict()
        settings_file = None
        if isinstance(input, str):
            ext = os.path.splitext(input)[1]
            assert ext == '.yaml', f'unrecognized file type for: {input}'
            with open(input) as fp:
                input_dict = yaml.safe_load(fp)
            #
            settings_file = input
        elif isinstance(input, dict):
            input_dict = input
        elif input is not None:
            assert False, 'got invalid input'
        #
        # override the entries with kwargs
        for k, v in kwargs.items():
            input_dict[k] = v
        #
        for key, value in input_dict.items():
            if key == 'include_files' and input_dict['include_files'] is not None:
                include_base_path = os.path.dirname(settings_file) if settings_file is not None else './'
                idict = self._parse_include_files(value, include_base_path)
                self.update(idict)
            else:
                self.__setattr__(key, value)
            #
        #
        # collect basic keys that are added during initialization
        # only these will be copied during call to basic_settings()
        self.basic_keys = list(self.keys())

    def basic_settings(self):
        '''this only returns the basic settings.
        sometimes, there is no need to copy the entire settings
        which includes the dataset_cache'''
        return ConfigDict({k:self[k] for k in self.basic_keys})
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    # pickling used by multiprocessing did not work without defining __getstate__
    def __getstate__(self):
        self.__dict__.copy()

    # this seems to be not required by multiprocessing
    def __setstate__(self, state):
        self.__dict__.update(state)

    def _initialize(self):
        # include additional files and merge with this dict
        self.include_files = None
        # execution pipeline type - currently only accuracy pipeline is defined
        self.pipeline_type = 'accuracy'
        # number of frames for inference
        self.num_frames = 10000 #50000
        # number of frames to be used for post training quantization / calibration
        self.calibration_frames = 25 #50
        # number of iterations to be used for post training quantization / calibration
        self.calibration_iterations = 25 #50
        # folder where benchmark configs are defined. this should be python importable
        self.configs_path = './configs'
        # folder where models are available
        self.models_path = '../edgeai-modelzoo/models'
        # path where compiled model artifacts are placed
        self.modelartifacts_path = './work_dirs/modelartifacts'
        # create your datasets under this folder
        self.datasets_path = f'./dependencies/datasets'
        # target_device indicates the SoC for which the model compilation will take place
        # see device_types for various devices in constants.TARGET_DEVICES_DICT
        # currently this field is for information only
        # the actual target device depends on the tidl_tools being used.
        self.target_device = None
        # important parameter. set this to 'pc' to do import and inference in pc
        # set this to 'evm' to run inference in device/soc. for inference on device run_import
        # below should be switched off and it is assumed that the artifacts are already created.
        self.target_machine = 'pc' #'evm' #'pc'
        # artifacts - suffix : attach this suffix to the run_dir where artifacts are created
        self.run_suffix = None
        # for parallel execution on pc only (cpu or gpu(. if you don't have gpu, these actual numbers don't matter,
        # but the size of the list determines the number of parallel processes
        # if you have gpu's these wil be used for CUDA_VISIBLE_DEVICES. eg. [0,1,2,3,0,1,2,3]
        self.parallel_devices = None #[0,1,2,3,0,1,2,3]
        # quantization bit precision
        self.tensor_bits = 8 #8 #16 #32
        # runtime_options can be specified as a dict. eg {'accuracy_level': 0}
        self.runtime_options = None
        # run import of the model - only to be used in pc - set this to False for evm
        # for pc this can be True or False
        self.run_import = True
        # run inference - for inferene in evm, it is assumed that the artifaacts folders are already available
        self.run_inference = True
        # run only models for which the results are missing. if this is False, all configs will be run
        self.run_missing = True
        # detection threshold
        # recommend 0.3 for best fps, 0.05 for accuracy measurement
        self.detection_threshold = 0.3
        # detection  - top_k boxes that go into nms
        # (this is an intermediate set, not the final number of boxes that are kept)
        # # recommend 200 for best fps, 500 for accuracy measurement
        self.detection_top_k = 200
        # detection  - NMS threshold to be used for detection
        self.detection_nms_threshold = None
        # max number of final detections
        self.detection_keep_top_k = None
        # save detection, segmentation output
        self.save_output = False
        # number of frames for example output
        self.num_output_frames = 50 #None
        # wild card list to match against model_path, model_id or model_type - if null, all models wil be shortlisted
        # only models matching these criteria will be considered - even for model_selection
        #   examples: ['onnx'] ['tflite'] ['mxnet'] ['onnx', 'tflite']
        #   examples: ['resnet18.onnx', 'resnet50_v1.tflite'] ['classification'] ['imagenet1k'] ['torchvision'] ['coco']
        #   examples: [cl-0000, od-2020, ss-2580, cl-3090, cl-3520, od-5120, ss-5710, cl-6360, od-8050, od-8220, od-8420, ss-8610, kd-7060, op-7200]
        # it can also be a number, which indicates a predefined shortlist, and a fraction of the models will be selected
        # 0 means no models, 1 means 1 model, 15 means roughly 15% of models, 100 means all the models.
        #   examples: 1
        #   examples: 15
        #   examples: 30
        self.model_selection = None
        # exclude the models that matches with this
        self.model_exclusion = None
        # wild card list to match against the tasks. it null, all tasks will be run
        # example: ['classification', 'detection', 'segmentation', 'human_pose_estimation', 'detection_3d']
        # example: ['classification']
        self.task_selection = None
        # wild card list to match against runtime name. if null, all runtimes will be considered
        # example: ['onnxrt', 'tflitert', 'tvmdlr']
        # example: ['onnxrt']
        self.runtime_selection = None
        # session types to use for each model type
        self.session_type_dict = {'onnx': 'onnxrt', 'tflite': 'tflitert', 'mxnet': 'tvmdlr'}
        # dataset type to use if there are multiple variants for each dataset
        # example: {'imagenet':'imagenetv1'}
        # example: {'imagenet':'imagenetv2c'}
        self.dataset_type_dict = None
        # dataset_selection can be a list of dataset categories for which the models will be run
        self.dataset_selection = None
        # whether to load the datasets or not. set to False or null to load no datasets
        # set to True to try and load all datasets (the dataset folders must be available in ./dependencies/datasets).
        # for selective loading, provide a list of dataset names such as
        # ['imagenet', 'coco', 'cocoseg21', 'ade20k', 'cocokpts', 'kitti_lidar_det', 'ti-robokit_semseg_zed1hd', 'ycbv']
        self.dataset_loading = True
        # which configs to run from the default list. example [0,10] [10,null] etc.
        self.config_range = None
        # logging of the import, infer and the accuracy. set to False to disable it.
        self.enable_logging = True
        # verbose mode - print out more information
        self.verbose = False
        # capture_log mode - capture and redirect details logs to log file
        self.capture_log = False
        # enable use of experimental models - the actual model files are not available in modelzoo
        self.experimental_models = False
        # rewrite results with latest params if the result exists
        self.rewrite_results = False
        # it defines if we want to use udp postprocessing in human pose estimation.
        # Paper ref: Huang et al. The Devil is in the Details: Delving into Unbiased
        # Data Processing for Human Pose Estimation (CVPR 2020).
        self.with_udp = True
        # it will add horizontally flipped images in info_dict and run inference over the flipped image also
        self.flip_test = False
        # the transformations that needs to be applied to the model itself. Note: this is different from pre-processing transforms
        self.model_transformation_dict = None
        # include perfsim stats in the report or not
        self.report_perfsim = False
        # use TIDL offload to speedup inference
        self.tidl_offload = True
        # input optimization to improve FPS: False or None
        # None will cause the default value set in sessions.__init__ to be used.
        self.input_optimization = None
        # how many parent folders to be included from the model path, while creating the run_dir
        # default value is defined in basert_session.py
        self.run_dir_tree_depth = None

    def _parse_include_files(self, include_files, include_base_path):
        input_dict = {}
        include_files = utils.as_list(include_files)
        for include_file in include_files:
            append_base = not (include_file.startswith('/') and include_file.startswith('./'))
            include_file = os.path.join(include_base_path, include_file) if append_base else include_file
            with open(include_file) as ifp:
                idict = yaml.safe_load(ifp)
                input_dict.update(idict)
            #
        #
        return input_dict

