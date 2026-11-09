# Download counts

The `downloads` badge in the README shows the **total** from the newest point in
[`download-history.json`](download-history.json): `bundle.tar.gz` downloads plus
`statement.json` downloads. [`download-history.yml`](../workflows/download-history.yml)
adds a point every Monday 00:00 Philippine time (it can also be run by hand) and opens a
pull request with the new point and the badge.

## What is counted

- **`bundle.tar.gz`**: one release per rules bundle (`bundle-<digest>`), never replaced.
  The engine downloads it when a scan does not have that bundle cached yet. GitHub's
  count is complete back to the first bundle (16 June 2026).
- **`statement.json`**: the signed channel pointer on the `channel-<name>` release. The
  engine fetches it on every online scan (unless rule updates are turned off).

Both are file downloads, not users. A scan with no cached bundle (common on CI runners)
downloads both files.

## Why the total is higher than GitHub's own counts

Each rules publish replaces `statement.json` on the channel release, and GitHub resets a
replaced file's download count to zero. Since 10 November 2026,
[`publish.yml`](../workflows/publish.yml) reads that count just before replacing the
file and adds it to the line `Downloads of replaced statements: N` in the channel
release's notes. The snapshot adds those numbers back (`statements_replaced`), so the
total keeps the downloads that GitHub no longer shows.

On 10 November 2026 the release counts on GitHub summed to 4,588. The total was 6,511,
which includes **1,929** carried over.

## Where the 1,929 comes from

It is the `channel-production` `statement.json` count on GitHub just before the
9 November 2026 publish replaced it. The snapshot taken that morning (00:00 Philippine
time) had recorded 1,924; five more arrived before the publish.

## What is not counted

The total is a minimum.

- `statement.json` downloads replaced by publishes before 4 September 2026, when the
  snapshots started: never recorded.
- The four publishes between 21 September and 20 October 2026: the snapshot before each
  one shows at least 412, 150, 524 and 200 downloads (1,286 in all), which are not added.
