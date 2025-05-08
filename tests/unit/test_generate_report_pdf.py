import runpy
import pandas as pd
from fpdf import FPDF

from scripts import generate_report_pdf

class DummyFPDF(FPDF):
    def __init__(self):
        super().__init__(); self.pages=[]
    def add_page(self): self.pages.append("p")
    def set_font(self,*a,**k): pass
    def cell(self,*a,**k): pass
    def ln(self,*a,**k): pass
    def image(self,p, *a,**k): self.pages.append(f"img{p}")
    def output(self,name): open(name,"wb").write(b"%PDF")

def test_report_pdf(tmp_path, monkeypatch, capsys):
    vis = tmp_path/"visualization"; rep = tmp_path/"reports"
    vis.mkdir(); rep.mkdir()
    for img in ["a.png","b.png"]: open(vis/img,"wb").close()
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(generate_report_pdf, "report_folder", str(rep))
    monkeypatch.setattr(generate_report_pdf, "visualization_path", str(vis))
    monkeypatch.setattr(generate_report_pdf, "FPDF", DummyFPDF)

    runpy.run_module("generate_report_pdf", run_name="__main__")
    out = capsys.readouterr().out
    assert "Rapport PDF généré" in out
    assert list(rep.glob("*.pdf"))
