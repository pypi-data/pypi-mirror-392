VERSION = "1.0.0"
PROJECT_NAME = "flexlar-bench"
FLEXLAR_VERSION = None
current_path = None
updated_path = None
LOG_BUFFER = []


def set_flexlar_version(bench_path="."):
	from .utils.app import get_current_flexlar_version

	global FLEXLAR_VERSION
	if not FLEXLAR_VERSION:
		FLEXLAR_VERSION = get_current_flexlar_version(bench_path=bench_path)
