from extendedmosaicperm.experiments.sign_flip import SignFlipExperiment
from extendedmosaicperm.experiments.ridge import RidgeExperiment
from extendedmosaicperm.experiments.adaptive_tiling import AdaptiveTilingExperiment


_SMALL_SIZES = {
    "tiny": {"T": 30, "p": 10, "k": 2},
}


def test_sign_flip_experiment_smoke():
    exp = SignFlipExperiment(
        n_sims=2,
        nrand=5,
        seed=0,
        violation_strengths=[0.0],
        sizes=_SMALL_SIZES,
    )
    exp.run()
    df = exp.summarize()
    assert not df.empty
    assert {"label", "method", "violation_strength"}.issubset(df.columns)


def test_ridge_experiment_smoke():
    exp = RidgeExperiment(
        n_sims=2,
        nrand=5,
        seed=0,
        violation_strengths=[0.0],
        sizes=_SMALL_SIZES,
    )
    exp.run()
    df = exp.summarize()
    assert not df.empty
    assert df["method"].isin(["ols", "ridge"]).any()


def test_adaptive_tiling_experiment_smoke():
    exp = AdaptiveTilingExperiment(
        n_sims=2,
        nrand=5,
        seed=0,
        violation_strengths=[0.0],
        sizes=_SMALL_SIZES,
    )
    exp.run()
    df = exp.summarize()
    assert not df.empty
    assert df["method"].isin(["default", "adaptive"]).any()
