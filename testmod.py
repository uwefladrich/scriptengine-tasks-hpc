from scriptengine_hpc.module import modfunc_from_lmod, modfunc_from_environment_modules

module = modfunc_from_lmod("/home/sm_uflad/Projects/lmod") or modfunc_from_environment_modules()

module("list")
