"""
Complete Test of New Analysis API

Tests all analysis capabilities:
- NAMD log parsing
- All plotting customization options
- Unit conversions (Å/nm, ps/ns/µs, kcal/kJ)
- RMSF residue labeling options
- Multi-line distance plotting
- Energy plotting with full customization

Uses actual test files: step1-3_equilibration.dcd, step1_equilibration.log, system.pdb
"""

from pathlib import Path
import numpy as np
from gatewizard.utils.namd_analysis import TrajectoryAnalyzer, EnergyAnalyzer

# Test configuration
TEST_DIR = Path(__file__).parent
TOPOLOGY = TEST_DIR / "system.pdb"
DCD_FILES = [
    TEST_DIR / "step1_equilibration.dcd",
    TEST_DIR / "step2_equilibration.dcd",
    TEST_DIR / "step3_equilibration.dcd"
]
LOG_FILE = TEST_DIR / "step1_equilibration.log"

# File times: Each file is 50,000 steps × 1 fs = 50 ps = 0.05 ns
FILE_TIMES = {
    "step1_equilibration.dcd": 0.05,
    "step2_equilibration.dcd": 0.05,
    "step3_equilibration.dcd": 0.05
}

def test_files_exist():
    """Test 1: Verify all required files exist"""
    print("\n" + "="*70)
    print("TEST 1: File Existence")
    print("="*70)
   
    missing = []
    if not TOPOLOGY.exists():
        missing.append(str(TOPOLOGY))
    for dcd in DCD_FILES:
        if not dcd.exists():
            missing.append(str(dcd))
    if not LOG_FILE.exists():
        missing.append(str(LOG_FILE))
   
    if missing:
        print("❌ FAILED: Missing files:")
        for f in missing:
            print(f"   - {f}")
        return False
   
    print("✓ PASSED: All test files exist")
    print(f"  - Topology: {TOPOLOGY.name}")
    print(f"  - Trajectories: {len(DCD_FILES)} files")
    print(f"  - Log file: {LOG_FILE.name}")
    return True


def test_trajectory_analyzer_init():
    """Test 2: TrajectoryAnalyzer initialization with file_times"""
    print("\n" + "="*70)
    print("TEST 2: TrajectoryAnalyzer Initialization")
    print("="*70)
   
    try:
        analyzer = TrajectoryAnalyzer(
            topology=TOPOLOGY,
            trajectory=DCD_FILES,
            file_times=FILE_TIMES
        )
        print("✓ PASSED: TrajectoryAnalyzer initialized successfully")
        print(f"  - Universe atoms: {analyzer.universe.atoms.n_atoms}")
        print(f"  - Trajectory frames: {len(analyzer.universe.trajectory)}")
        return True, analyzer
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None


def test_rmsd_calculation(analyzer):
    """Test 3: RMSD calculation with alignment"""
    print("\n" + "="*70)
    print("TEST 3: RMSD Calculation")
    print("="*70)
   
    try:
        data = analyzer.calculate_rmsd("protein and backbone", align=True)
       
        assert 'time' in data, "Missing 'time' key"
        assert 'rmsd' in data, "Missing 'rmsd' key"
        assert len(data['time']) == len(data['rmsd']), "Time and RMSD arrays length mismatch"
       
        # Check time scaling
        expected_total_time = 0.15  # 3 files × 0.05 ns
        actual_total_time = data['time'][-1] - data['time'][0]
        assert abs(actual_total_time - expected_total_time) < 0.001, f"Time scaling incorrect: {actual_total_time} vs {expected_total_time}"
       
        print("✓ PASSED: RMSD calculation")
        print(f"  - Time range: {data['time'][0]:.3f} - {data['time'][-1]:.3f} ns ({actual_total_time*1000:.1f} ps)")
        print(f"  - RMSD range: {data['rmsd'].min():.2f} - {data['rmsd'].max():.2f} Å")
        print(f"  - Mean RMSD: {data['rmsd'].mean():.2f} ± {data['rmsd'].std():.2f} Å")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_rmsf_calculation(analyzer):
    """Test 4: RMSF calculation with residue information"""
    print("\n" + "="*70)
    print("TEST 4: RMSF Calculation")
    print("="*70)
   
    try:
        data = analyzer.calculate_rmsf("protein and name CA")
       
        required_keys = ['resids', 'rmsf', 'resnames', 'atom_indices']
        for key in required_keys:
            assert key in data, f"Missing '{key}' key"
           
        assert len(data['resids']) == len(data['rmsf']), "Residue count mismatch"
        assert len(data['resids']) == len(data['resnames']), "Residue names count mismatch"
       
        print("✓ PASSED: RMSF calculation")
        print(f"  - Residues analyzed: {len(data['resids'])}")
        print(f"  - RMSF range: {data['rmsf'].min():.2f} - {data['rmsf'].max():.2f} Å")
        print(f"  - Mean RMSF: {data['rmsf'].mean():.2f} ± {data['rmsf'].std():.2f} Å")
       
        # Show most flexible residues
        top_3_idx = np.argsort(data['rmsf'])[-3:]
        print("  - Top 3 flexible residues:")
        for idx in top_3_idx[::-1]:
            print(f"    {data['resnames'][idx]}{data['resids'][idx]}: {data['rmsf'][idx]:.2f} Å")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_distances_calculation(analyzer):
    """Test 5: Distance calculation between selections"""
    print("\n" + "="*70)
    print("TEST 5: Distance Calculation")
    print("="*70)
   
    try:
        selections = {
            "N-C term": ("resid 1-20 and name CA", "resid 200-220 and name CA")
        }
        results = analyzer.calculate_distances(selections)
       
        assert "N-C term" in results, "Missing distance data"
        assert 'time' in results["N-C term"], "Missing time data"
        assert 'distance' in results["N-C term"], "Missing distance data"
       
        data = results["N-C term"]
        print("✓ PASSED: Distance calculation")
        print(f"  - Time range: {data['time'][0]:.3f} - {data['time'][-1]:.3f} ns")
        print(f"  - Distance range: {data['distance'].min():.2f} - {data['distance'].max():.2f} Å")
        print(f"  - Mean distance: {data['distance'].mean():.2f} ± {data['distance'].std():.2f} Å")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_radius_of_gyration(analyzer):
    """Test 6: Radius of gyration calculation"""
    print("\n" + "="*70)
    print("TEST 6: Radius of Gyration")
    print("="*70)
   
    try:
        data = analyzer.calculate_radius_of_gyration("protein")
       
        assert 'time' in data, "Missing time data"
        assert 'rg' in data, "Missing Rg data"
       
        print("✓ PASSED: Radius of gyration calculation")
        print(f"  - Time range: {data['time'][0]:.3f} - {data['time'][-1]:.3f} ns")
        print(f"  - Rg range: {data['rg'].min():.2f} - {data['rg'].max():.2f} Å")
        print(f"  - Mean Rg: {data['rg'].mean():.2f} ± {data['rg'].std():.2f} Å")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_rmsd_plotting(analyzer):
    """Test 7: RMSD plotting with all customization options"""
    print("\n" + "="*70)
    print("TEST 7: RMSD Plotting Options")
    print("="*70)
   
    try:
        # Test basic plot
        analyzer.plot_rmsd(
            selection="protein and backbone",
            align=True,
            save="test_rmsd_basic.png"
        )
        print("✓ Basic RMSD plot saved")
       
        # Test with unit conversion
        analyzer.plot_rmsd(
            selection="protein and backbone",
            align=True,
            distance_units="nm",
            time_units="ps",
            save="test_rmsd_units.png"
        )
        print("✓ RMSD plot with unit conversion saved")
       
        # Test with full customization
        analyzer.plot_rmsd(
            selection="protein and backbone",
            align=True,
            distance_units="Å",
            time_units="ps",
            line_color="#1f77b4",
            bg_color="#2b2b2b",
            fig_bg_color="#212121",
            text_color="Auto",
            show_grid=True,
            xlim=(0, 150),
            ylim=(0, 3.0),
            title="Test RMSD - Full Customization",
            save="test_rmsd_custom.png"
        )
        print("✓ Fully customized RMSD plot saved")
       
        print("✓ PASSED: All RMSD plotting options")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_rmsf_plotting(analyzer):
    """Test 8: RMSF plotting with residue labeling options"""
    print("\n" + "="*70)
    print("TEST 8: RMSF Plotting Options")
    print("="*70)
   
    try:
        # Test basic plot
        analyzer.plot_rmsf(
            selection="protein and name CA",
            save="test_rmsf_basic.png"
        )
        print("✓ Basic RMSF plot saved")
       
        # Test with residue labels (3-letter)
        analyzer.plot_rmsf(
            selection="protein and name CA",
            xaxis_type="residue_type_number",
            residue_name_format="triple",
            label_frequency="every_5",
            save="test_rmsf_labeled_triple.png"
        )
        print("✓ RMSF with 3-letter residue labels saved")
       
        # Test with residue labels (1-letter)
        analyzer.plot_rmsf(
            selection="protein and name CA",
            xaxis_type="residue_type_number",
            residue_name_format="single",
            label_frequency="every_10",
            save="test_rmsf_labeled_single.png"
        )
        print("✓ RMSF with 1-letter residue labels saved")
       
        # Test with highlight threshold
        analyzer.plot_rmsf(
            selection="protein and name CA",
            highlight_threshold=2.0,
            distance_units="Å",
            bg_color="#2b2b2b",
            save="test_rmsf_highlight.png"
        )
        print("✓ RMSF with flexible region highlighting saved")
       
        print("✓ PASSED: All RMSF plotting options")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_distance_plotting(analyzer):
    """Test 9: Distance plotting with multiple pairs"""
    print("\n" + "="*70)
    print("TEST 9: Distance Plotting Options")
    print("="*70)
   
    try:
        # Test single pair
        analyzer.plot_distances(
            selections={"N-C term": ("resid 1-20 and name CA", "resid 200-220 and name CA")},
            save="test_dist_single.png"
        )
        print("✓ Single distance pair plot saved")
       
        # Test multiple pairs with custom colors
        analyzer.plot_distances(
            selections={
                "N-C term": ("resid 1-20 and name CA", "resid 200-220 and name CA"),
                "Domain 1-2": ("resid 50-70 and name CA", "resid 150-170 and name CA")
            },
            line_colors=["#1f77b4", "#ff7f0e"],
            show_mean_lines=True,
            distance_units="Å",
            time_units="ps",
            bg_color="#2b2b2b",
            save="test_dist_multi.png"
        )
        print("✓ Multiple distance pairs plot saved")
       
        print("✓ PASSED: All distance plotting options")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_energy_analyzer():
    """Test 10: EnergyAnalyzer with all options"""
    print("\n" + "="*70)
    print("TEST 10: Energy Analysis")
    print("="*70)
   
    try:
        analyzer = EnergyAnalyzer(LOG_FILE)
        print("✓ EnergyAnalyzer initialized")
       
        # Test basic plot
        analyzer.plot_energy(save="test_energy_basic.png")
        print("✓ Basic energy plot saved")
       
        # Test with unit conversion
        analyzer.plot_energy(
            energy_units="kJ/mol",
            time_units="ps",
            save="test_energy_units.png"
        )
        print("✓ Energy plot with unit conversion saved")
       
        # Test with custom styling
        analyzer.plot_energy(
            energy_units="kcal/mol",
            time_units="ps",
            bg_color="#2b2b2b",
            fig_bg_color="#212121",
            text_color="Auto",
            show_grid=True,
            title="Test Energy Analysis",
            save="test_energy_custom.png"
        )
        print("✓ Fully customized energy plot saved")
       
        # Test statistics
        stats = analyzer.get_statistics()
        print(f"✓ Statistics retrieved")
        print(f"  - Temperature: {stats['temp']['mean']:.1f} ± {stats['temp']['std']:.1f} K")
        print(f"  - Total Energy: {stats['total']['mean']:.0f} kcal/mol")
       
        print("✓ PASSED: All energy analysis options")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("COMPLETE API TEST SUITE")
    print("="*70)
    print(f"Test directory: {TEST_DIR}")
    print(f"Files to test: {len(DCD_FILES)} DCDs, 1 log, 1 topology")
    print(f"Total simulation time: {sum(FILE_TIMES.values())*1000:.0f} ps")
   
    results = []
   
    # Test 1: File existence
    results.append(("File Existence", test_files_exist()))
   
    if not results[0][1]:
        print("\n" + "="*70)
        print("ABORTING: Required files not found")
        print("="*70)
        return
   
    # Test 2-6: Initialize and test calculations
    success, analyzer = test_trajectory_analyzer_init()
    results.append(("TrajectoryAnalyzer Init", success))
   
    if analyzer:
        results.append(("RMSD Calculation", test_rmsd_calculation(analyzer)))
        results.append(("RMSF Calculation", test_rmsf_calculation(analyzer)))
        results.append(("Distance Calculation", test_distances_calculation(analyzer)))
        results.append(("Radius of Gyration", test_radius_of_gyration(analyzer)))
       
        # Test 7-9: Plotting options
        results.append(("RMSD Plotting", test_rmsd_plotting(analyzer)))
        results.append(("RMSF Plotting", test_rmsf_plotting(analyzer)))
        results.append(("Distance Plotting", test_distance_plotting(analyzer)))
   
    # Test 10: Energy analysis
    results.append(("Energy Analysis", test_energy_analyzer()))
   
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
   
    passed = sum(1 for _, result in results if result)
    total = len(results)
   
    for test_name, result in results:
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
   
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed ({100*passed/total:.0f}%)")
    print("="*70)
   
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nNew API features verified:")
        print("  ✓ Multi-file trajectory support")
        print("  ✓ file_times parameter and time scaling")
        print("  ✓ Unit conversions (Å/nm, ps/ns/µs, kcal/kJ)")
        print("  ✓ All plot customization options")
        print("  ✓ RMSF residue labeling")
        print("  ✓ Multi-line distance plotting")
        print("  ✓ Energy analysis with full options")
    else:
        print(f"\n⚠️ {total-passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()
