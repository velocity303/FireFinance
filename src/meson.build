# Install Python sources
pkgdatadir = join_paths(get_option('prefix'), 'share', meson.project_name(), 'src')

python_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'data_manager.py',
  'models.py',
  'price_service.py',
  'chart_widget.py'  # <--- NEW FILE
]

install_data(python_sources, install_dir: pkgdatadir)

# Create the executable launch script
conf = configuration_data()
conf.set('PYTHON', py_installation.path())
conf.set('PKGDATADIR', pkgdatadir)

configure_file(
  input: 'firefinance.in',
  output: 'firefinance',
  configuration: conf,
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x'
)