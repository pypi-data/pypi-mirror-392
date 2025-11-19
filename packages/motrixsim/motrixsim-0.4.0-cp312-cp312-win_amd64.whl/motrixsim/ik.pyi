# Copyright (C) 2020-2025 Motphys Technology Co., Ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import builtins
import numpy
import numpy.typing
import typing
from motrixsim import SceneData, SceneModel

class DlsSolver:
    r"""
    Use Damped Least Squares (DLS) method to solve inverse kinematics problem.
    
    DLS is a robust optimization method that adds regularization to handle singular
    configurations and improve numerical stability. It's also known as Levenberg-Marquardt
    for IK applications.
    
    Args:
       max_iter (int): Maximum number of iterations (default: 100).
       step_size (float): Step size for each iteration (default: 0.5).
       tolerance (float): Tolerance for convergence (default: 1e-3).
       damping (float): Damping parameter for regularization (default: 1e-3).
           - Small values (1e-6 to 1e-4): Near Gauss-Newton behavior
           - Medium values (1e-4 to 1e-2): Good balance for most applications
           - Large values (1e-2 to 1.0): More stable but slower convergence
    """
    def __new__(cls, max_iter:builtins.int=100, step_size:builtins.float=0.5, tolerance:builtins.float=0.0010000000474974513, damping:builtins.float=0.0010000000474974513) -> DlsSolver: ...
    def solve(self, ik_model:typing.Any, data:SceneData, target_pose:typing.Any) -> numpy.typing.NDArray[numpy.float32]:
        r"""
        Solve the IK problem for the given chain and target pose.
        
        Args:
            ik_model (IkChain): The IK model. Currently only `IkChain` is supported.
            data (SceneData): The scene data containing the current state.
            target_pose (NDarray[float]): The target pose the end effector want to reach.
                It is a 7-element array with (x, y, z, i, j, k, w) format.
        
        Returns:
          A numpy array with shape `(data.shape, ik_model.num_dof_pos + 2,)`. For each row, the
          first element is the number of iterations used, the second element is the final
          residual, and the remaining elements are the solved DOF positions.
        """

class GaussNewtonSolver:
    r"""
    Use gauss newton iterative method to solve inverse kinematics problem.
    
    Args:
       max_iter (int): Maximum number of iterations (default: 100).
       step_size (float): Step size for each iteration (default: 0.5).
       tolerance (float): Tolerance for convergence (default: 1e-3).
    """
    def __new__(cls, max_iter:builtins.int=100, step_size:builtins.float=0.5, tolerance:builtins.float=0.0010000000474974513) -> GaussNewtonSolver: ...
    def solve(self, ik_model:typing.Any, data:SceneData, target_pose:typing.Any) -> numpy.typing.NDArray[numpy.float32]:
        r"""
        Solve the IK problem for the given chain and target pose.
        
        Args:
            ik_model (IkChain): The IK model. Currently only `IkChain` is supported.
            data (SceneData): The scene data containing the current state.
                target_pose (NDarray[float]): The target pose the end effector want to reach.  It is
                a 7-element array with (x, y, z, i, j, k, w) format.
        
        Returns:
          A numpy array with shape `(data.shape, ik_model.num_dof_pos + 2,)`. For each row, the
          first element   is the number of iterations used, the second element is the final
          residual, and the   remaining elements are the solved DOF positions.
        """

class IkChain:
    r"""
    Represents a kinematic chain for inverse kinematics (IK) solving.
    
    Args:
        model (SceneModel): The scene model containing the kinematic structure.
        end_link (str): The name of the end link of the IK chain.
        start_link (Optional[str]): The name of the start link of the IK chain. If not provided,
            the root link will be used.
        end_effector_offset (Optional[ndarray]): A 7-element array representing the end-effector
            offset as a pose (x, y, z, i, j, k, w) in end link's local space. If not provided, no
            offset will be applied.
    Raises:
       RuntimeError: If the IK chain contains unsupported joint types. (Currently only hinge and
            slider are supported.)
    """
    def __new__(cls, model:SceneModel, end_link:builtins.str, start_link:typing.Optional[builtins.str]=None, end_effector_offset:typing.Optional[typing.Any]=None) -> IkChain: ...

