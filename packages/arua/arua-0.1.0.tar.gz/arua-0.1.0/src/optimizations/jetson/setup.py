from setuptools import setup, Extension
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name="grok_gpu",
    ext_modules=[
        CUDAExtension(
            "grok_gpu",
            sources=[
                "semantic_grain_kernel.cu",
                "prng_kernel.cu",
                "grok_extension.cpp",
            ],
            extra_compile_args={"cxx": ["-g"], "nvcc": ["-O2"]},
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
