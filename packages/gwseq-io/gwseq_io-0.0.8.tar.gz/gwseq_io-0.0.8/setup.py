from glob import glob
from pybind11 import get_include
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup


def is_lib_available(name):
    import subprocess, tempfile
    tests = {
        "curl": "#include <curl/curl.h>\nint main() { curl_version(); return 0; }",
        "z": "#include <zlib.h>\nint main() { zlibVersion(); return 0; }"}
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = f"{tmp_dir}/test.cpp"
        out_file = f"{tmp_dir}/test"
        with open(test_file, "w") as f:
            f.write(tests[name])
        try:
            cmd = ["c++", test_file, f"-l{name}", "-o", out_file]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception:
            return False

libraries = []
extra_compile_args = []
if is_lib_available("curl"):
    libraries.append("curl")
else:
    extra_compile_args.append("-DNO_CURL")
if is_lib_available("z"):
    libraries.append("z")
else:
    extra_compile_args.append("-DNO_ZLIB")


ext_modules = [
    Pybind11Extension(
        "gwseq_io",
        sources=[
            "gwseq_io/binding.cpp",
        ],
        include_dirs=[
            "gwseq_io/",
            get_include(),
        ],
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        language="c++",
        cxx_std=17,
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    data_files=[(
        "gwseq_io",
            glob("gwseq_io/**/*.c", recursive=True) +
            glob("gwseq_io/**/*.h", recursive=True) +
            glob("gwseq_io/**/*.cpp", recursive=True) +
            glob("gwseq_io/**/*.hpp", recursive=True)
        )
    ],
)
