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

from jai_benchmark import utils
from jai_benchmark import datasets

from . import classification
from . import detection
from . import segmentation
from . import human_pose_estimation


def get_configs(settings, work_dir):
    # load the datasets - it is done only once and re-used for all configs
    if settings.dataset_cache is None:
        settings.dataset_cache = datasets.get_datasets(settings)
    #

    pipeline_configs = {}
    # merge all the config dictionaries
    pipeline_configs.update(classification.get_configs(settings, work_dir))
    pipeline_configs.update(detection.get_configs(settings, work_dir))
    pipeline_configs.update(segmentation.get_configs(settings, work_dir))
    pipeline_configs.update(human_pose_estimation.get_configs(settings,work_dir))
    if settings.experimental_models:
        from . import classification_experimental
        from . import detection_experimental
        from . import segmentation_experimental
        # now get the experimental configs
        pipeline_configs.update(classification_experimental.get_configs(settings, work_dir))
        pipeline_configs.update(detection_experimental.get_configs(settings, work_dir))
        pipeline_configs.update(segmentation_experimental.get_configs(settings, work_dir))
    #
    return pipeline_configs


def select_configs(settings, work_dir, session_name=None):
    task_selection = utils.as_list(settings.task_selection)
    pipeline_configs = get_configs(settings, work_dir)
    pipeline_configs = {pipeline_id:pipeline_config for pipeline_id, pipeline_config in pipeline_configs.items() \
            if pipeline_config['task_type'] in task_selection}
    if session_name is not None:
        pipeline_configs = {pipeline_id:pipeline_config for pipeline_id, pipeline_config in pipeline_configs.items() \
                if pipeline_config['session'].peek_param('session_name') == session_name}
    #
    return pipeline_configs


def print_all_configs(pipeline_configs=None, enable_print=False):
    if enable_print:
        for k, v in sorted(pipeline_configs.items()):
            model_name = k + '-' + v['session'].kwargs['session_name']
            print("'{}',".format(model_name))
    return




