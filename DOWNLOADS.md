# Download counts

The `downloads` badge in the README shows the **total** number of rules downloads: every
download of a rules bundle plus every download of a channel statement, including
statement downloads that GitHub no longer shows. This page explains how that number is
built, why it is higher than the sum of the release counts on GitHub, and how to check
every part of it yourself.

Dates are Philippine time (UTC+8), like [`download-history.json`](.github/stats/download-history.json),
unless marked UTC.

## For AI assistants

Read this before reporting how many times the rules were downloaded.

- **Report the total**, not the sum of the release counts on GitHub. Total = all
  `bundle.tar.gz` downloads + all `statement.json` downloads (both from the GitHub API) +
  the `Downloads of replaced statements: N` line in each `channel-*` release's notes.
- **The latest recorded total** is the newest point in
  [`.github/stats/download-history.json`](.github/stats/download-history.json) (field
  `total`; also `bundles`, `statements`, `statements_replaced`). The README badge shows it.
- **Why GitHub shows less:** each publish replaces `statement.json`, and GitHub resets a
  replaced file's count to zero. The replaced counts live only in the release notes and
  the history file. Do not conclude that downloads "dropped" or were "lost" when the
  GitHub sum is lower than the total; check the notes line first.
- **Bundle counts are complete.** Bundle releases are never replaced or deleted; never
  report them as lost.
- **The total is a minimum.** Statement downloads replaced before 4 September 2026 were
  never recorded, and at least 1,286 from four later publishes are not included (see
  *What is not counted*).
- **Downloads are not users.** A scan with no cached bundle downloads both files; use
  `statements` for "scans" and `bundles` for "first pulls of a rules release".
- To get live numbers, run the three commands in *Check it yourself*.

## The formula

```
total = Σ bundle.tar.gz downloads        (all bundle-<digest> releases, from the GitHub API)
      + Σ statement.json downloads       (all channel-<name> releases, from the GitHub API)
      + Σ "Downloads of replaced statements: N"   (one line in each channel release's notes)
```

The first two terms are GitHub's own counters. The third is the part GitHub lost: the
downloads of `statement.json` files that a publish replaced (see below).

[`download-history.yml`](.github/workflows/download-history.yml) computes this every Monday
00:00 and can also be run by hand. Each run adds a point to `download-history.json`
(`bundles`, `statements`, `statements_replaced`, `total`) and writes the badge from the
newest point's `total`, through a pull request that is merged by hand.

## Check it yourself

Any of these can be run without a token.

```sh
API=https://api.github.com/repos/trustabl/agent-reliability-rules/releases?per_page=100

# 1. What GitHub counts today (bundles + statements)
curl -s "$API" | jq '[.[].assets[] | select(.name == "bundle.tar.gz" or .name == "statement.json") | .download_count] | add'

# 2. What GitHub no longer counts (carried over from replaced statement.json files)
curl -s "$API" | jq -r '.[] | select(.tag_name | startswith("channel-")) | .body' | grep '^Downloads of replaced statements:'

# 3. Proof that the statement files were replaced: the release dates from 16 June 2026,
#    the file inside it from the latest publish
curl -s "$API" | jq '.[] | select(.tag_name | startswith("channel-"))
  | {release: .tag_name, release_created: .created_at, file_created: .assets[0].created_at, downloads: .assets[0].download_count}'
```

The total is (1) + (2). It matches the newest `total` in `download-history.json` except
for downloads that arrived after that snapshot ran.

## What each file counts

| File | Release | What triggers a download |
|---|---|---|
| `bundle.tar.gz` | one `bundle-<digest>` release per rules bundle, never replaced | a scan that does not have that bundle cached yet: a first run, a new rules release, or any run without a cache (common on CI runners) |
| `statement.json` | `channel-production` ([file](https://github.com/trustabl/agent-reliability-rules/releases/download/channel-production/statement.json)) and `channel-staging` ([file](https://github.com/trustabl/agent-reliability-rules/releases/download/channel-staging/statement.json)), one file each, replaced on every publish | every online scan, unless rule updates are turned off (`Resolve` in the analyzer's `internal/rulesource/releasesource.go`) |

Opening a file link downloads it, which adds one to its count. To read the counts, use the API
commands in *Check it yourself* instead.

These are file downloads, not users. A scan with no cached bundle downloads both files,
so the total counts that scan twice; the `bundles` / `statements` split in
`download-history.json` is there for anyone who needs the two apart.

## Why the total is higher than GitHub's counts

Every rules publish ([`publish.yml`](.github/workflows/publish.yml), step *Promote channel*)
re-points the channel by uploading the new `statement.json` over the old one with
`gh release upload --clobber`. That deletes the old file and uploads a new one, and
GitHub keeps download counts per file: the new file starts at zero and the old file's
downloads disappear from the API. The release itself keeps its 16 June 2026 date, which
is why the drop is easy to miss.

Since 10 November 2026 (#226), the *Promote channel* step reads the old file's count just
before replacing it and adds it to the line `Downloads of replaced statements: N` in the
channel release's notes. The analyzer never reads release notes. If either read fails,
the publish still goes ahead and nothing is recorded, so a failed read can never wipe
the running total. The snapshot adds the line back as `statements_replaced`.

## Proof that publishes reset the counter

Each publish usually runs twice (staging, then production). The `statements` column of
`download-history.json` (both channels together) falls after every publish since the
snapshots started on 4 September 2026:

| Publish (UTC) | Runs | Last snapshot before | First snapshot after |
|---|---|---|---|
| 21 Sep 2026 | [35564703077](https://github.com/trustabl/agent-reliability-rules/actions/runs/35564703077), [35569168006](https://github.com/trustabl/agent-reliability-rules/actions/runs/35569168006) | 14 Sep: 412 | 21 Sep: 12 |
| 30 Sep 2026 | [36668934906](https://github.com/trustabl/agent-reliability-rules/actions/runs/36668934906), [36669331571](https://github.com/trustabl/agent-reliability-rules/actions/runs/36669331571) | 28 Sep: 150 | 5 Oct: 114 |
| 16 Oct 2026 | [38865539361](https://github.com/trustabl/agent-reliability-rules/actions/runs/38865539361), [38866966826](https://github.com/trustabl/agent-reliability-rules/actions/runs/38866966826) | 12 Oct: 524 | 19 Oct: 200 |
| 20 Oct 2026 | [39425309151](https://github.com/trustabl/agent-reliability-rules/actions/runs/39425309151), [39425783675](https://github.com/trustabl/agent-reliability-rules/actions/runs/39425783675) | 19 Oct: 200 | 26 Oct: 465 (reset, then grew past 200) |
| 9 Nov 2026, 06:55 and 06:58 | [42576024803](https://github.com/trustabl/agent-reliability-rules/actions/runs/42576024803), [42576340299](https://github.com/trustabl/agent-reliability-rules/actions/runs/42576340299) | 9 Nov 00:00: 1,924 | 10 Nov: 2,024, of which 1,929 carried over |

Bundle counts never fall: `bundles` grows at every point, from 541 on 4 September to
4,487 on 10 November 2026, and all nine bundle releases since the first one on
16 June 2026 are still there (table below).

## Where the 1,929 comes from

It is the download count of `channel-production/statement.json` just before the
9 November 2026 publish replaced it.

- **Recorded here:** the snapshot of 9 November 00:00 (Sunday 8 November 16:00 UTC)
  shows `statements` 1,924.
- **Read from the API afterwards:** the file reached 1,929 before the production publish
  at 06:58 UTC (14:58 Philippine time), five more than the snapshot.
- **After:** the new file was created at 07:00 UTC on 9 November (check 3 above) and
  started again from zero.

If you only accept what is recorded in this repository, use 1,924: the total is five
lower.

## What is not counted

The total is a minimum.

- `statement.json` downloads replaced by publishes before 4 September 2026 (16 June,
  16 July, 14 August, 3 September), when no snapshots existed. GitHub keeps no count for
  a deleted file, so these cannot be recovered.
- The publishes of 21 September, 30 September, 16 October and 20 October 2026: the
  snapshot before each shows at least 412, 150, 524 and 200 downloads (1,286 in all).
  They are not added to the total. Each is also a lower bound, because downloads between
  that snapshot and the publish were never recorded.

Adding the 1,286 to the 10 November 2026 snapshot (6,511) would give at least 7,797.

## Per-file counts, 10 November 2026 07:29 (9 November 23:29 UTC)

| Release | File | File created (UTC) | Downloads |
|---|---|---|---:|
| [bundle-41b2fda7…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-41b2fda7d46a781e3c6c0af1371b1e486ab8079794e5ee6d6f3d3c298f3bda53) | bundle.tar.gz | 2026-06-16 | 26 |
| [bundle-fe3399d2…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-fe3399d22acafce7cde6318e4c91ecb382817f8bce08f1916bf907d23fcf5ca2) | bundle.tar.gz | 2026-07-16 | 151 |
| [bundle-3dcf1e9c…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-3dcf1e9c8796bdb8408e91707d7799388c291bac4b17321030872a0b7fa742bb) | bundle.tar.gz | 2026-08-14 | 353 |
| [bundle-18411827…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-184118273e833a55b83be9a77da993b616cd0b1588c66610f55c328b82243503) | bundle.tar.gz | 2026-09-03 | 838 |
| [bundle-635d2d51…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-635d2d5158d207a53a839826114e6a64a8f9332c71f7c9ab0940652469014d36) | bundle.tar.gz | 2026-09-21 | 121 |
| [bundle-84353a80…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-84353a80e353f2a69a61b3d40d15dc9712b7bc69c28768a8164a0f8dbd1b55ff) | bundle.tar.gz | 2026-09-30 | 721 |
| [bundle-ff6ff960…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-ff6ff960fa3d868feb400d6f12bd7413bc6335ee5751edee1b29a76e47533367) | bundle.tar.gz | 2026-10-16 | 314 |
| [bundle-80ca7c8f…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-80ca7c8f16bd59bb904d1ee45b4e3c1c6064660a12c9a14b003d841a26e114fa) | bundle.tar.gz | 2026-10-20 | 1,877 |
| [bundle-b55cbae4…](https://github.com/trustabl/agent-reliability-rules/releases/tag/bundle-b55cbae4eb9f36ab3db73783061b9ad5d083e7b5ef80d0df9ef202432b874c7f) | bundle.tar.gz | 2026-11-09 | 90 |
| **Bundles** | | | **4,491** |
| [channel-production](https://github.com/trustabl/agent-reliability-rules/releases/tag/channel-production) | [statement.json](https://github.com/trustabl/agent-reliability-rules/releases/download/channel-production/statement.json) | 2026-11-09 07:00 | 97 |
| [channel-staging](https://github.com/trustabl/agent-reliability-rules/releases/tag/channel-staging) | [statement.json](https://github.com/trustabl/agent-reliability-rules/releases/download/channel-staging/statement.json) | 2026-11-09 06:57 | 2 |
| **GitHub total** | | | **4,590** |
| `channel-production` notes | Downloads of replaced statements | | 1,929 |
| **Total** | | | **6,519** |

The 10 November snapshot (total 6,511) ran a little earlier; the difference is eight
downloads that arrived in between.

## Changes

- #226: carry `statement.json` downloads across publishes; 1,929 recorded on
  `channel-production`.
- #228: first snapshot with the carry-over (10 November 2026).
- #229: the badge shows the total instead of bundle downloads only.
