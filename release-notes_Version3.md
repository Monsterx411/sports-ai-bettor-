# Release v4.0.1

Summary
-------
Short summary (1–2 lines) of v4.0.1: what's new and why users should upgrade.

Highlights
----------
- Key improvement or feature A
- Key improvement or feature B
- Important bug fix or breaking change (if any)

Full changelog
--------------
<!-- REPLACE THIS BLOCK with the generated changelog or PR list -->
- Placeholder: replace with actual PR/commit list generated from your repository

Upgrade / Migration notes
-------------------------
- If you use the config file: rename config.example.json -> config.json and update the new "odds_source" key (if applicable).
- Backwards-incompatible change: CLI argument `--model` now expects a path to a model bundle directory, not a single file. (Adjust if not applicable.)

How to get it
-------------
- Docker: docker pull monsterx411/sports-ai-bettor:v4.0.1
- GitHub release: download the asset named `sports-ai-bettor-v4.0.1.tar.gz`
- From source: git checkout tags/v4.0.1

Assets included
---------------
- sports-ai-bettor-v4.0.1.tar.gz — prebuilt binary bundle
- sports-ai-bettor-v4.0.1-wheel.whl — Python wheel (if applicable)
- changelog.txt — plain text changelog

Testing / QA notes
------------------
- Tested on Ubuntu 22.04 and macOS (specify version)
- Integration tests: data-fetcher, model-trainer, bet-executor — (list status)
- Known issues:
  - Occasional latency spikes when scraping SourceY (investigating)

Contributors
------------
Thanks to the contributors for this release:
- @alice
- @bob
- @carol
- (add real contributor handles)

Contact / Support
-----------------
Report regressions or security issues at https://github.com/Monsterx411/sports-ai-bettor-/issues/new

Signed-off-by: Monsterx411