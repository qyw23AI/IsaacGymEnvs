"""Load the converted mybot_v3 USD in Isaac Lab and step PhysX on the selected device."""

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--steps", type=int, default=240)
parser.add_argument(
    "--auto-close",
    action="store_true",
    help="Close Isaac Sim as soon as the requested simulation steps finish.",
)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app_launcher = AppLauncher(args, multi_gpu=False)
simulation_app = app_launcher.app

import omni.usd
from pxr import UsdPhysics

import isaaclab.sim as sim_utils


def main():
    usd_path = Path(__file__).with_name("mybot_v3.usd").resolve()
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1.0 / 120.0, device=args.device))
    sim_utils.GroundPlaneCfg().func("/World/Ground", sim_utils.GroundPlaneCfg())
    sim_utils.DomeLightCfg(intensity=2000.0).func("/World/Light", sim_utils.DomeLightCfg(intensity=2000.0))
    robot_cfg = sim_utils.UsdFileCfg(usd_path=str(usd_path))
    robot_cfg.func("/World/mybot_v3", robot_cfg, translation=(0.0, 0.0, 0.65))
    sim.set_camera_view(eye=[2.2, 2.2, 1.6], target=[0.0, 0.0, 0.55])
    print(f"MYBOT_SPAWNED path={usd_path}", flush=True)
    sim.reset()
    print("MYBOT_RESET_OK", flush=True)

    stage = omni.usd.get_context().get_stage()
    robot_prim = stage.GetPrimAtPath("/World/mybot_v3")
    if not robot_prim.IsValid():
        raise RuntimeError(f"Robot prim was not loaded from {usd_path}")
    joint_count = sum(1 for prim in stage.Traverse() if prim.IsA(UsdPhysics.Joint))
    for step in range(args.steps):
        sim.step()
        if (step + 1) % 10 == 0 or step + 1 == args.steps:
            print(f"MYBOT_STEP {step + 1}/{args.steps}", flush=True)

    print(
        f"MYBOT_SIM_OK steps={args.steps} device={sim.device} "
        f"joints={joint_count} asset={usd_path}",
        flush=True,
    )
    if not args.auto_close:
        print("MYBOT_VIEWER_READY Close the Isaac Sim window when you are done.", flush=True)
        while simulation_app.is_running():
            simulation_app.update()

if __name__ == "__main__":
    main()
    simulation_app.close()
