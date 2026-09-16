# X02 execution-body provenance addendum

The prereg-extracted body hash is
`1e567d93fa558b0cb2fc5a3e4735215d03479b662d73491e2068ec8daf96b41a`.
The actual successful `/tmp/x02_body.log` hash is
`db852a55828cb19c6056946619b0345118e7b28cf2cfad6e204b97e0d734a26e`.

The diff is limited to: (1) checking master injectivity over the three distinct
seeds rather than nine profile-duplicated pairs; (2) recording both hashes and
the script-only correction honestly; (3) adding the prior failure explanation;
and (4) removing the heredoc terminator from the Python body. No profile, K,
seed, block, sampling or decoder semantic changed. The X02 focused review
independently reran strong/45/140/seed1450 and matched every field.

P5 must reconstruct the selected point from the frozen formulas and accepted
runner; it must not execute or import the X02 body.
