import argparse
from pygbm import GBM_simulator
import matplotlib.pyplot as plt
import numpy as np


# simulate the GBM path using specified method
def simulate(y0, mu, sigma, path, T, N, method):
    simulator = GBM_simulator(y0, mu, sigma)
    t_values, y_values = simulator.simulate_path(T, N, method)
    simulator.plot_path(t_values, y_values)
    plt.savefig(path+"/path_simulation.png", dpi=300, bbox_inches="tight")

# compare the GBM path simulated using milstein method and the analytic method
def compare(y0, mu, sigma, path, T, N):
    simulator = GBM_simulator(y0, mu, sigma)
    simulator.simulate_compare(T, N, 7689, ["exact_method", "euler_method"])
    plt.savefig(path+"/comparision.png", dpi=300, bbox_inches="tight")

# simulate the GBM for a number of times and plot the sample mean
def sample_sim(y0, mu, sigma, path, T, N, sample_num):
    simulator = GBM_simulator(y0, mu, sigma)
    samples = list()
    for i in range(sample_num):
        t_values, y_values = simulator.simulate_path(T, N, seed = i)
        samples.append(y_values)
        plt.plot(t_values , y_values , color = "grey", alpha = 0.1)
    plt.plot(t_values, np.mean(samples, axis = 0), color = "red", label = "sample mean")
    plt.xlabel("Time")
    plt.ylabel("Y(t)")
    plt.legend()
    plt.title("Simulated Sample Geometric Brownian Motion Paths")
    plt.savefig(path+"/sample_simulation.png", dpi=300, bbox_inches="tight")


##### now we set up the command-line interface
def main():
    # build the command-line interface for the package
    parser = argparse.ArgumentParser(description="GBM CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # command1 (for simulate)
    parser_simulate = subparsers.add_parser("simulate", help="simulate the GBM path using analytical method")
    parser_simulate.add_argument("--y0", type=float, required=True, help="inital value of the process")
    parser_simulate.add_argument("--mu", type=float, required=True, help="mu of the GBM process")
    parser_simulate.add_argument("--sigma", type=float, required=True, help="sigma of the GBM process")
    parser_simulate.add_argument("--path", type=str, required=True, help="directory to store the plot")
    parser_simulate.add_argument("--T", type=float, default=1.0, help="number of dvision of the time duration")
    parser_simulate.add_argument("--N", type=int,  default=2**7, help="total duartion of the process")
    parser_simulate.add_argument("--method", type=str, default="exact_method", help="method for simulation: exact_method, euler_method, milstein_method")

    # command2 (for compare)
    parser_compare = subparsers.add_parser("compare", help="compare the GBM path simulated using milstein method and the analytic method")
    parser_compare.add_argument("--y0", type=float, required=True, help="inital value of the process")
    parser_compare.add_argument("--mu", type=float, required=True, help="mu of the GBM process")
    parser_compare.add_argument("--sigma", type=float, required=True, help="sigma of the GBM process")
    parser_compare.add_argument("--path", type=str, required=True, help="directory to store the plot")
    parser_compare.add_argument("--T", type=float, default=1.0, help="number of dvision of the time duration")
    parser_compare.add_argument("--N", type=int,  default=2**7, help="total duartion of the process")

    # command3 (for sample_sim)
    parser_sample_sim = subparsers.add_parser("sample_sim", help="simulate the GBM for a number of times and plot the sample mean")
    parser_sample_sim.add_argument("--y0", type=float, required=True, help="inital value of the process")
    parser_sample_sim.add_argument("--mu", type=float, required=True, help="mu of the GBM process")
    parser_sample_sim.add_argument("--sigma", type=float, required=True, help="sigma of the GBM process")
    parser_sample_sim.add_argument("--path", type=str, required=True, help="directory to store the plot")
    parser_sample_sim.add_argument("--T", type=float, default=1.0, help="number of dvision of the time duration")
    parser_sample_sim.add_argument("--N", type=int,  default=2**7, help="total duartion of the process")
    parser_sample_sim.add_argument("--sample_num", type=int, default=10000, help="sample num")

    # decide which command (function) to execute when getting some input from the command line
    args = parser.parse_args()
    if args.command == "simulate":
        simulate(args.y0, args.mu, args.sigma, args.path, args.T, args.N, args.method)
    if args.command == "compare":
        compare(args.y0, args.mu, args.sigma, args.path, args.T, args.N)
    if args.command == "sample_sim":
        sample_sim(args.y0, args.mu, args.sigma, args.path, args.T, args.N, args.sample_num)

# just ensure the CLI runs
if __name__ == "__main__":
    main()