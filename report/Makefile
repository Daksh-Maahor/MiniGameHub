LATEX = pdflatex
BIBTEX = bibtex

TARGET = report

all: $(TARGET).pdf

$(TARGET).pdf: $(TARGET).tex
	$(LATEX) $(TARGET)
	$(LATEX) $(TARGET)  # Run twice for references

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.bbl *.blg

cleanall: clean
	rm -f $(TARGET).pdf

view: $(TARGET).pdf
	xdg-open $(TARGET).pdf &

.PHONY: all clean cleanall view
