project('firefinance',
  version : '0.1.0',
  meson_version : '>= 0.59.0',
)

python = import('python')
py_installation = python.find_installation('python3')

# Standard variables
prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
pythondir = py_installation.get_install_dir()

subdir('src')

gnome = import('gnome')