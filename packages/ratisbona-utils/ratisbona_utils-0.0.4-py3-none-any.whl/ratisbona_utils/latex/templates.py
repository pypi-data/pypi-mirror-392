def open_dialogue_document(title: str) -> str:
    return (
"""\\documentclass[a4paper]{article}
\\usepackage[ngerman]{babel}
\\usepackage[dvipsnames]{xcolor}
\\usepackage[export]{adjustbox} % loads also graphicx
\\usepackage{amsmath}
\\usepackage{emoji}
\\usepackage{fontspec}
\\usepackage{dialogue}
\\usepackage{wasysym}
\\usepackage{minted}
\\usepackage{cprotect}
\\usepackage[colorlinks=true, allcolors=TealBlue]{hyperref}
\\usepackage{longtable,tabu}
\\setlength{\\parindent}{0ex}
\\setlength{\\parskip}{1ex}
\\setminted{breaklines=true, breakanywhere=true}

\\newcommand{\\uliji}[1]{
  {\\setmainfont{Noto Color Emoji}[Renderer=Harfbuzz]{#1}}
}


\\author{Ulrich Schwenk}
\\title{""" + title +"""}

\\begin{document}
\\setlength{\\tabulinesep}{6pt}
\\maketitle
\\newpage
"""
    )

def close_dialogue_document() -> str:
    return "\n\\end{document}\n"