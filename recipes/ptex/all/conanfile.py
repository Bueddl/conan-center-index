from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.43.0"


class PtexConan(ConanFile):
    name = "ptex"
    description = "Ptex is a texture mapping system developed by Walt Disney " \
                  "Animation Studios for production-quality rendering."
    license = "BSD-3-Clause"
    topics = ("ptex", "texture-mapping")
    homepage = "https://ptex.us"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PTEX_BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["PTEX_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        cmake_target = "Ptex_dynamic" if self.options.shared else "Ptex_static"
        self.cpp_info.set_property("cmake_file_name", "ptex")
        self.cpp_info.set_property("cmake_target_name", "Ptex::{}".format(cmake_target))
        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["_ptex"].libs = ["Ptex"]
        if not self.options.shared:
            self.cpp_info.components["_ptex"].defines.append("PTEX_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_ptex"].system_libs.append("pthread")
        self.cpp_info.components["_ptex"].requires = ["zlib::zlib"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ptex"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ptex"
        self.cpp_info.names["cmake_find_package"] = "Ptex"
        self.cpp_info.names["cmake_find_package_multi"] = "Ptex"
        self.cpp_info.components["_ptex"].set_property("cmake_target_name", "Ptex::{}".format(cmake_target))
        self.cpp_info.components["_ptex"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_ptex"].names["cmake_find_package_multi"] = cmake_target
