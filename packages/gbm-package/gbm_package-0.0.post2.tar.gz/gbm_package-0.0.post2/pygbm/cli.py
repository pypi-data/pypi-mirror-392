import argparse
import os
import sys
import subprocess
from .gbm_simulation import GBMSimulator

def simulate_(y0, mu, sigma, T, N, output):
    """Simulate"""
    simulator = GBMSimulator(y0=1.0, mu=0.05, sigma=0.2)
    t_values, y_values = simulator.simulate_path(T=1.0, N=100)
    ax = simulator.plot_path(t_values, y_values)
    ax.figure.savefig(output)
    print(f"Saved plot to {output}")

    # Try to open the image file automatically (cross-platform)
    try:
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", output], check=False)
        elif os.name == "nt":  # Windows
            os.startfile(output)
        elif os.name == "posix":  # Linux
            subprocess.run(["xdg-open", output], check=False)
    except Exception as e:
        print(f"⚠️ Could not open file automatically: {e}")
    

def main():
    """
    Main function for the CLI tool.
    """
    parser = argparse.ArgumentParser(description="GBM CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Sub-command for simulating process
    simulate_plot = subparsers.add_parser("simulate", help="Simulate and plot GBM.")
    simulate_plot.add_argument("--y0", type=float, required=True, help="y0")
    simulate_plot.add_argument("--mu", type=float, required=True, help="mu")
    simulate_plot.add_argument("--sigma", type=float, required=True, help="sigma")
    simulate_plot.add_argument("--T", type=float, required=True, help="T")
    simulate_plot.add_argument("--N", type=float, required=True, help="N")
    simulate_plot.add_argument("--output", type=str, required=True, help="Output filename for plot")


    args = parser.parse_args()

    if args.command == "simulate":
        simulate_(args.y0, args.mu, args.sigma, args.T, args.N, args.output)


if __name__ == "__main__":
    main()
