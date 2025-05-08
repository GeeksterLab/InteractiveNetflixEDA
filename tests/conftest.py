# tests/conftest.py
import os
import sys
import types
import pytest

# Crée le dossier utilisé par default dans visualize_analyse_data.py
os.makedirs("/Users/shaina/Desktop/My_projects/APP/Netflix_EDA/visualization", exist_ok=True)

# 1) Ajoute la racine du projet au PYTHONPATH
sys.path.insert(0, os.getcwd())

# 2) Stub global de 'fpdf'
class DummyFPDF:
    def __init__(self, *args, **kwargs):
        self.pages = []
    def add_page(self): pass
    def set_font(self, *args, **kwargs): pass
    def cell(self, *args, **kwargs): pass
    def ln(self, *args, **kwargs): pass
    def image(self, *args, **kwargs): pass
    def output(self, name):
        with open(name, "wb") as f:
            f.write(b"%PDF-1.4 dummy")
    # **Ajout de la méthode manquante**
    def set_auto_page_break(self, auto=True, margin=0):
        # Pas besoin de faire quoi que ce soit, juste pour passer l'appel
        return

fpdf_mod = types.ModuleType("fpdf")
fpdf_mod.FPDF = DummyFPDF
sys.modules["fpdf"] = fpdf_mod
sys.modules["fpdf.fpdf"] = fpdf_mod

# 3) Stub global de 'streamlit'
st_mod = types.ModuleType("streamlit")
class _DummySidebar:
    def radio(self, *args, **kwargs): return args[1][0]
    def selectbox(self, *args, **kwargs): return args[1][0]
class _DummySt:
    sidebar = _DummySidebar()
    def markdown(self, *a, **k): pass
    def title(self, *a, **k): pass
    def header(self, *a, **k): pass
    def write(self, *a, **k): pass
    def dataframe(self, *a, **k): pass
    def plotly_chart(self, *a, **k): pass
    def selectbox(self, *a, **k): return a[1][0]
    def cache_data(self, fn): return fn

st_instance = _DummySt()
for attr in ("markdown","title","header","write","dataframe","plotly_chart","selectbox","cache_data"):
    setattr(st_mod, attr, getattr(st_instance, attr))
setattr(st_mod, "sidebar", st_instance.sidebar)
sys.modules["streamlit"] = st_mod

@pytest.fixture(autouse=True)
def no_leak_env(monkeypatch):
    yield
