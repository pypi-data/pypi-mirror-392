"""Setup script for jxc-python package."""

from pathlib import Path

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.dist import Distribution

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:  # pragma: no cover - wheel not installed
    _bdist_wheel = None


class CustomBuildExt(build_ext):
    """Run the custom build helper before packaging."""

    def run(self):  # noqa: D401 - setuptools hook
        repo_root = Path(__file__).resolve().parent
        helper_exists = any(repo_root.glob('jxc/helper*.so')) or any(
            repo_root.glob('jxc/helper*.dylib')
        )

        if getattr(self, 'inplace', False):
            if not helper_exists:
                print(
                    "Editable install detected; helper extension not prebuilt. "
                    "Run `make build-wheel` to regenerate the binary helper."
                )
            else:
                print("Editable install detected; using existing helper extension.")
            return

        if not helper_exists:
            raise RuntimeError(
                "Binary helper missing. Run `make build-wheel` (which generates "
                "the helper via scripts/generate_helper.sh) before packaging."
            )

        print("Helper extension already present; skipping custom build step.")


class BinaryDistribution(Distribution):
    """Mark the distribution as containing platform-specific binaries."""

    def has_ext_modules(self):  # pragma: no cover - simple override
        return True


class CustomBDistWheel(_bdist_wheel):
    """Ensure wheels are tagged as platform-specific."""

    def finalize_options(self):  # pragma: no cover - simple override
        super().finalize_options()
        self.root_is_pure = False


cmdclass = {
    'build_ext': CustomBuildExt,
}
if _bdist_wheel is not None:
    cmdclass['bdist_wheel'] = CustomBDistWheel


if __name__ == '__main__':
    setup(
        cmdclass=cmdclass,
        distclass=BinaryDistribution,
    )
