"""Main Launcher & Biological SNN Diagnostics for Fruit Fly Simulation.

Runs the 3D Fruit Fly Football visualizer and provides optional
closed-loop Drosophila connectome SNN diagnostics.
"""

from __future__ import annotations

import sys
import time
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import webbrowser

from src.server_3d import start_3d_server, broadcast_telemetry

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FruitFlyPipeline")


def run_pipeline(
    dry_run: bool = True,
    max_steps: Optional[int] = None,
    gui: bool = False,
    web_3d: bool = False,
    device: Optional[str] = None,
    force_regenerate: bool = False,
    cooldown_ms: float = 250.0,
) -> Dict[str, Any]:
    """Executes the closed-loop Drosophila connectome pipeline."""
    import cv2
    import numpy as np
    import torch
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    from src.data_engine import load_or_generate_connectome, DEFAULT_CONNECTOME_PATH
    from src.brain_sim import DrosophilaLIFBrain, BrainStepResult
    from src.game_interface import ScreenGrabber, VisualMotionProcessor, GameActionController

    def create_telemetry_table(
        fps: float,
        latency_ms: float,
        total_spikes: int,
        mean_voltage: float,
        sensory_spikes: int,
        action: Optional[str],
        confidence: float,
        dry_run: bool,
    ) -> Table:
        table = Table(title="Drosophila SNN Telemetry", expand=True, border_style="cyan")
        table.add_column("Metric", style="bold white")
        table.add_column("Value", style="bold yellow")
        table.add_row("Loop Execution Rate", f"{fps:.1f} FPS")
        table.add_row("Brain Step Latency", f"{latency_ms:.2f} ms")
        table.add_row("Sensory Spikes (T4/T5)", f"{sensory_spikes} spikes")
        table.add_row("Total Active Spikes", f"{total_spikes} / 2,000 neurons")
        table.add_row("Mean Membrane Potential", f"{mean_voltage:.3f} mV")
        table.add_row(
            "Current Motor Action",
            f"[{'bold green' if action else 'dim'}]{action or 'IDLE'}[/]",
        )
        table.add_row("Action Confidence", f"{confidence:.3f}")
        table.add_row("Mode", "[cyan]Biological SNN Simulation[/]")
        return table

    def create_motor_bars(motor_rates: Dict[str, float], threshold: float) -> Panel:
        lines = []
        actions = [
            ("TURN_LEFT", motor_rates.get("swipe_left", 0.0), "bright_blue"),
            ("TURN_RIGHT", motor_rates.get("swipe_right", 0.0), "bright_cyan"),
            ("ESCAPE_JUMP", motor_rates.get("jump", 0.0), "bright_green"),
            ("BANK_ROLL", motor_rates.get("roll", 0.0), "bright_yellow"),
        ]
        for name, rate, color in actions:
            bar_len = min(30, int(rate * 150))
            bar = "█" * bar_len + "░" * (30 - bar_len)
            th_indicator = " [*]" if rate >= threshold else ""
            lines.append(f"{name:<12} [{color}]{bar}[/] {rate:.3f}{th_indicator}")
        return Panel("\n".join(lines), title="Descending Motor Clusters (DN Activity)", border_style="green")

    def create_sensory_bars(flow_rates: Dict[str, float]) -> Panel:
        lines = []
        quads = [
            ("Leftward Flow", flow_rates.get("left", 0.0), "blue"),
            ("Rightward Flow", flow_rates.get("right", 0.0), "cyan"),
            ("Upward Looming", flow_rates.get("up", 0.0), "green"),
            ("Downward Flow", flow_rates.get("down", 0.0), "yellow"),
        ]
        for name, mag, color in quads:
            bar_len = min(25, int(mag * 20))
            bar = "■" * bar_len + "·" * (25 - bar_len)
            lines.append(f"{name:<16} [{color}]{bar}[/] {mag:.2f}")
        return Panel("\n".join(lines), title="Optic Lobe Flow Intensity", border_style="blue")

    # Start 3D WebGL server if requested
    if web_3d:
        try:
            start_3d_server(port=8080)
            webbrowser.open("http://localhost:8080")
            logger.info("Opened 3D Drosophila Flight Arena in browser: http://localhost:8080")
        except Exception as e:
            logger.warning(f"Could not start 3D Web server: {e}")

    # 1. Connectome Data Engine
    connectome = load_or_generate_connectome(
        DEFAULT_CONNECTOME_PATH, force_regenerate=force_regenerate
    )

    # 2. SNN Brain Simulator
    brain = DrosophilaLIFBrain(
        connectome_data=connectome,
        device=device,
        motor_threshold=0.05,
    )

    # 3. Vision & Interface Components
    grabber = ScreenGrabber()
    vision_processor = VisualMotionProcessor(grid_size=32, gain=2.5)
    action_controller = GameActionController(
        cooldown_ms=cooldown_ms,
        dry_run=dry_run,
    )

    # 4. Neural Telemetry Buffer for GUI Raster Plot
    raster_history = []  # Last 80 timesteps of 2000-neuron spike vectors
    max_history = 80

    console = Console()
    step_count = 0
    start_time = time.time()
    last_frame_time = time.time()

    # Track metrics for return summary
    summary = {
        "steps_executed": 0,
        "total_spikes": 0,
        "actions_triggered": [],
        "mean_fps": 0.0,
    }

    try:
        with Live(console=console, refresh_per_second=20, transient=True) as live:
            while max_steps is None or step_count < max_steps:
                step_start = time.perf_counter()

                # A. Frame Acquisition (Synthetic stimulus generator)
                cycle = (step_count // 20) % 4
                dir_cue = ["left", "right", "up", "down"][cycle]
                bgr_frame = grabber.generate_synthetic_frame(stimulus_direction=dir_cue)

                # B. Visual Motion Processing (Optic Flow -> Poisson Spikes)
                sensory_spikes, flow_rates, downsampled_gray = vision_processor.process_frame(bgr_frame)

                # C. Drosophila SNN Step
                brain_start = time.perf_counter()
                brain_res: BrainStepResult = brain.step(sensory_spikes)
                brain_latency_ms = (time.perf_counter() - brain_start) * 1000.0

                # D. Game Action Controller Dispatch
                executed = False
                if brain_res.action:
                    executed = action_controller.execute_action(brain_res.action)
                    if executed:
                        summary["actions_triggered"].append(brain_res.action)

                # E. Broadcast to 3D WebGL Arena if active
                if web_3d:
                    broadcast_telemetry({
                        "action": brain_res.action if executed else None,
                        "spikes": brain_res.total_spikes_count,
                        "voltage": brain_res.mean_voltage,
                        "motor_rates": brain_res.motor_rates,
                        "optic_flow": flow_rates,
                    })

                # E. Real-time Telemetry Calculations
                now = time.time()
                fps = 1.0 / max(1e-5, now - last_frame_time)
                last_frame_time = now

                step_count += 1
                summary["steps_executed"] = step_count
                summary["total_spikes"] += brain_res.total_spikes_count

                # Update Rich Layout
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="body", ratio=1),
                )
                header_text = Text(
                    "Fruit Fly (Drosophila) Visual-Motor Connectome SNN Telemetry",
                    style="bold bright_white on dark_blue",
                    justify="center",
                )
                layout["header"].update(Panel(header_text, style="dark_blue"))

                table = create_telemetry_table(
                    fps=fps,
                    latency_ms=brain_latency_ms,
                    total_spikes=brain_res.total_spikes_count,
                    mean_voltage=brain_res.mean_voltage,
                    sensory_spikes=brain_res.sensory_spikes_count,
                    action=brain_res.action if executed else None,
                    confidence=brain_res.confidence,
                    dry_run=dry_run,
                )

                motor_panel = create_motor_bars(brain_res.motor_rates, brain.motor_threshold)
                sensory_panel = create_sensory_bars(flow_rates)

                layout["body"].split_row(
                    Layout(table, ratio=2),
                    Layout(motor_panel, ratio=2),
                    Layout(sensory_panel, ratio=2),
                )
                live.update(layout)

                # F. Optional OpenCV HUD
                if gui:
                    # 1. Visual Feed HUD
                    vis_color = cv2.applyColorMap(downsampled_gray, cv2.COLORMAP_VIRIDIS)
                    vis_large = cv2.resize(vis_color, (256, 256), interpolation=cv2.INTER_NEAREST)

                    # 2. Raster Plot
                    spikes_np = brain_res.spikes.cpu().numpy()
                    raster_history.append(spikes_np)
                    if len(raster_history) > max_history:
                        raster_history.pop(0)

                    # Render raster image (2000 neurons vertical x 80 timesteps horizontal)
                    raster_mat = np.stack(raster_history, axis=1)  # (2000, T)
                    raster_small = (raster_mat * 255).astype(np.uint8)
                    raster_img = cv2.resize(raster_small, (320, 256), interpolation=cv2.INTER_NEAREST)
                    raster_color = cv2.applyColorMap(raster_img, cv2.COLORMAP_BONE)

                    # Annotate regions (Sensory: 0-300, CX: 300-1700, Motor: 1700-2000)
                    cv2.line(raster_color, (0, int(256 * (300 / 2000))), (320, int(256 * (300 / 2000))), (255, 0, 0), 1)
                    cv2.line(raster_color, (0, int(256 * (1700 / 2000))), (320, int(256 * (1700 / 2000))), (0, 0, 255), 1)

                    hud = np.hstack([vis_large, raster_color])
                    cv2.imshow("Drosophila Connectome SNN HUD", hud)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                # Sleep slightly if step completed faster than 30 FPS target
                elapsed = time.perf_counter() - step_start
                if elapsed < 0.020:
                    time.sleep(0.020 - elapsed)

    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user interrupt.")
    finally:
        if gui:
            cv2.destroyAllWindows()

    total_time = max(1e-5, time.time() - start_time)
    summary["mean_fps"] = step_count / total_time
    logger.info(
        f"Pipeline finished: {step_count} steps executed in {total_time:.2f}s "
        f"({summary['mean_fps']:.1f} FPS, {len(summary['actions_triggered'])} actions triggered)."
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description="Fruit Fly 3D Football Simulation & Connectome SNN")
    parser.add_argument("--port", type=int, default=8080, help="Port for 3D simulation web server")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    parser.add_argument("--diagnostics", "--snn", action="store_true", help="Run biological Drosophila SNN connectome telemetry diagnostics in console")
    parser.add_argument("--gui", action="store_true", default=False, help="Open OpenCV neural raster and visual HUD")
    parser.add_argument("--steps", type=int, default=None, help="Number of simulation steps to run for diagnostics")
    parser.add_argument("--device", type=str, default=None, choices=["cuda", "cpu"], help="Compute device")
    parser.add_argument("--force-regenerate", action="store_true", default=False, help="Force regenerate connectome")
    parser.add_argument("--cooldown", type=float, default=250.0, help="Action refractory cooldown in ms")

    args = parser.parse_args()

    if args.diagnostics:
        run_pipeline(
            dry_run=True,
            max_steps=args.steps,
            gui=args.gui,
            web_3d=False,
            device=args.device,
            force_regenerate=args.force_regenerate,
            cooldown_ms=args.cooldown,
        )
    else:
        server = start_3d_server(port=args.port)
        actual_port = server.server_address[1]
        url = f"http://localhost:{actual_port}"
        print("\n" + "=" * 62)
        print("  FRUIT FLY 3D FOOTBALL ARENA IS RUNNING!")
        print(f"  --> Open in your browser: {url}")
        print("  Press Ctrl+C to stop the server.")
        print("=" * 62 + "\n", flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
