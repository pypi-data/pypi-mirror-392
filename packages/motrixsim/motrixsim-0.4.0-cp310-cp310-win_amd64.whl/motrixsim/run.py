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

import time

from absl import app, flags


def render_loop(
    phys_dt: float,
    render_fps: float,
    phys_step_func: callable,
    render_func: callable,
):
    """
    A simple render loop that runs the physics step function and render function at specified rates.

    Note:
        This function is blocking and will run indefinitely until interrupted.
    """
    phys_remain = phys_dt
    render_dt = 1.0 / render_fps

    phys_t0 = time.monotonic()
    while True:
        render_t0 = time.monotonic()
        phys_remain += time.monotonic() - phys_t0
        while phys_remain > phys_dt:
            phys_step_func()
            phys_remain -= phys_dt
        phys_t0 = time.monotonic()
        render_func()
        sleep_time = render_dt - (time.monotonic() - render_t0)
        if sleep_time > 0:
            time.sleep(sleep_time)


if __name__ == "__main__":
    _File = flags.DEFINE_string("file", None, "path to model", required=True)
    _Delay = flags.DEFINE_float("delay", 0.0, "delay seconds before starting the simulation", lower_bound=0.0)

    def main(argv):
        import motrixsim

        render_fps = 60.0
        path = _File.value
        print(f"Loading model from {path}")
        with motrixsim.render.RenderApp() as render:
            # Load the scene model
            model = motrixsim.load_model(path)
            # Create the render instance of the model
            render.launch(model)
            # Create the physics data of the model
            data = motrixsim.SceneData(model)

            if _Delay.value > 0.0:
                print(f"Waiting for {_Delay.value} seconds before starting the simulation...")
                time.sleep(_Delay.value)

            render_loop(
                phys_dt=model.options.timestep,
                render_fps=render_fps,
                phys_step_func=lambda: motrixsim.step(model, data),
                render_func=lambda: render.sync(data),
            )

    app.run(main)
