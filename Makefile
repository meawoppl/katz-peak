PYTHON ?= python3
FIGS = fig1_fit.pdf fig2_decomposition.pdf fig3_widmark.pdf fig4_katz_shift.pdf

all: katz_peak.pdf

fit.npz: digitize_fit.py data/ballmer_xkcd323.png
	$(PYTHON) digitize_fit.py

$(FIGS) numbers.txt &: figures.py fit.npz
	$(PYTHON) figures.py > numbers.txt

katz_peak.pdf: katz_peak.tex $(FIGS)
	pdflatex -interaction=nonstopmode -halt-on-error katz_peak.tex
	pdflatex -interaction=nonstopmode -halt-on-error katz_peak.tex

clean:
	rm -f *.aux *.log *.out fit.npz numbers.txt fig*.png $(FIGS)

.PHONY: all clean
