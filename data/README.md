# Source material

Put your source documents here, one subfolder per author. The folder
name becomes the author label used for filtering.

```
data/
  warren_buffett/
    1977_shareholder_letter.txt
    2008_shareholder_letter.txt
  ray_dalio/
    principles_summary.txt
  charlie_munger/
    psychology_of_human_misjudgment.txt
```

Supported formats: `.txt`, `.md`, `.pdf`.

## Where to find freely available material

Using public, freely-distributed primary sources keeps the project
legally clean **and** lets you open-source the whole repo. Good sources:

- **Warren Buffett** — Berkshire Hathaway publishes every annual
  shareholder letter for free on its official site. These are the
  richest, most quotable expression of his philosophy.
- **Ray Dalio** — released his *Principles* content publicly, plus
  many essays and articles.
- **Charlie Munger** — several of his famous speeches and talks have
  public transcripts.
- **General** — public interviews, conference talks, and op-eds these
  figures have authored often have official transcripts.

Save the text as `.txt` (cleanest for ingestion) or `.md`.

## A note on copyright

Only commit text you have the right to share. Their actual published
books are copyrighted: you can use your own legally-obtained copy for a
**local, personal** project, but do not commit those files to a public
repo or redistribute them. The `.gitignore` excludes PDFs by default to
help avoid this. Public letters, essays, and official transcripts are
the safe, shareable backbone for a portfolio version of this project.
