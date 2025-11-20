import xmle
import textwrap
import altair as alt
import pandas as pd


def test_rst():
    z = xmle.Show(
        textwrap.dedent("""

        Using reStructuredText
        ======================

        You can add sections of prose formatted using the reStructuredText markup
        syntax.  Just compose a string and pass it to the ``Show`` function, and
        you'll get a neatly formatted output.

        The default interpreter for ``str`` input to the ``Show`` function is
        reStructuredText, so you don't need to do anything special.  One caveat,
        though: the default for reStructuredText items is to step down headings by
        two levels.  So, the heading tag on this section will be ``h3`` not ``h1``.

        Deeper Headings are Stepped Down Also
        -------------------------------------

        So the heading on this section will be ``h4``.  Each block of
        reStructuredText is evaluated seperately, so knowledge of heading levels and
        which styles correspond to them is lost when evaluating a different string.

        Prevent Interpreting The First Heading as a Title
        =================================================

        If the first heading is at the beginning of the "document" and it is the
        only heading at that level, it is interpreted as the "title" and subsequent
        headings are stepped up a level.  This is how the standard docutils interpreter
        handles these cases.
        """)
    )
    assert isinstance(z, xmle.Elem)
    assert len(z) == 2
    assert z[0].tag == "div"
    assert z[1].tag == "div"
    assert len(z[0]) == 4
    assert z[0][0].tag == "h3"
    assert z[0][0].text == "Using reStructuredText"
    assert z[0][1].tag == "p"
    assert z[0][1].text.startswith("You can add sections")
    assert z[0][2].tag == "p"
    assert z[0][2].text.startswith("The default interpreter")
    assert z[0][3].tag == "div"
    assert len(z[0][3]) == 2
    assert z[0][3][0].tag == "h4"
    assert z[0][3][0].text == "Deeper Headings are Stepped Down Also"


def test_altair():
    fig = (
        alt.Chart(
            data=pd.DataFrame(
                {
                    "petalLength": [1.4, 1.4, 1.3, 1.5, 1.4, 1.7, 1.4, 1.5, 1.4, 1.5],
                    "petalWidth": [0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1],
                    "species": [
                        "setosa",
                        "setosa",
                        "setosa",
                        "setosa",
                        "setosa",
                        "versicolor",
                        "versicolor",
                        "versicolor",
                        "versicolor",
                        "versicolor",
                    ],
                }
            )
        )
        .mark_point()
        .encode(
            x="petalLength:Q",
            y="petalWidth:Q",
            color="species:N",
        )
    )
    z = xmle.Show(fig)
    assert isinstance(z, xmle.Elem)
    assert len(z) == 2
    assert z[0].tag == "div"
    assert z[1].tag == "script"
    assert z[1].text.startswith("vegaEmbed")
