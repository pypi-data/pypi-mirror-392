% labeldoc.cls - Custom document class for labels
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{labeldoc}[2024/12/07 Custom class for labels]

% Base class and default options
\LoadClass[a4paper,10pt]{article}

% Packages used
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{xparse}
\RequirePackage{enumitem}

% Default geometry
\geometry{top=2cm, bottom=2cm, left=2cm, right=2cm}

% Suppress page numbers
\pagestyle{empty}

% Define customizable font sizes
\newcommand{\labeldoctitlesize}{\Huge}
\newcommand{\labeldocsubtitlesize}{\Large}

\NewDocumentEnvironment{labelbox}{m m m o +b}{%
    \noindent
    \begin{minipage}[c][#2][c]{#1}
        \centering
        %\setlength{\parskip}{0pt} % No space between paragraphs
        \setlength{\fboxsep}{20pt} % No padding inside the frame
        \setlength{\fboxrule}{1pt} % Frame thickness
        \fbox{%
            \parbox[c][#2][c]{#1}{%
                {%
                    \centering
                    \textbf{\labeldoctitlesize #3}\\
                    %\vspace{0.3cm}
                    \IfValueTF{#4}{%
                        \textbf{\labeldocsubtitlesize #4}\\%\vspace{0.3cm}%
                    }{} % Include 4th parameter if provided
                }%
                \IfBlankF{#5}{%
                    \begin{itemize}[nosep]
                        #5
                    \end{itemize}
                } % Add body content provided by +b
            } % Properly close \parbox
        } % Properly close \fbox
    \end{minipage}
    \par
    \vspace{3cm} % Space between labels
}{}