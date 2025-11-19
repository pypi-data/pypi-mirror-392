from importlib.resources import files

_EXPERIMENTS = [
    "Exp1_freespacepathloss_vs_distance_graph.py",
    "Exp2_Observe_outage_probability_of_Rayleigh_rician_fading.py",
    "Exp3_Observe_outage_probability_of_siso_mimo_system.py",
    "Exp4_Power_delay_profile_multipath_frequency_selective.py",
    "Exp5_ber_performance_of_siso_system_coherent _detection.py",
    "Exp6_ber_performance_of_simo_system_with_mrc_egc.py",
    "Exp7_ber_performance_of_almouti_stbc.py",
    "Exp8_To_observe_channel_capacity_by_spatial_multiplexing_for_mimo.py",
    "Exp9_To_observe_ergodic_capacity_for_various_antenna_configureation.py",
    "Exp10_To_observe_ber_for_linear_detector.py",
    "Exp11_To_observe_ber_performance_of_maximum_likelihood.py",
]

def list():
    """List all experiment filenames with index."""
    print("\n📚 Available Experiments:\n")
    for idx, name in enumerate(_EXPERIMENTS, start=1):
        print(f"{idx}. {name}")
    print("\nUse: mabplotlib.show(index)\n")

def show(index: int) -> str:
    """Display the code for given experiment index."""
    idx = index - 1

    if idx < 0 or idx >= len(_EXPERIMENTS):
        raise IndexError(f"Index must be between 1 and {len(_EXPERIMENTS)}")

    filename = _EXPERIMENTS[idx]
    file_path = files("mabplotlib.experiments").joinpath(filename)
    code = file_path.read_text(encoding="utf-8")

    print(f"\n🔎 Showing code for {filename}:\n")
    print(code)
    # return code

def run(index: int):
    """Execute the experiment code in current Python session."""
    code = show(index)
    exec(code, globals())
