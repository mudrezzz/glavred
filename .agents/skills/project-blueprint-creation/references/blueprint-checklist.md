# Project Blueprint Checklist

Use this checklist before writing or updating Glavred project fixtures.

## Required Blueprint Sections

- Project profile: stable id/name, description, language, benchmark role.
- Author image: who writes, what experience is credible, what posture the author takes.
- Goals: why the blog exists and what every issue should support.
- Audience: project-level reader segment and value. Do not put canonical audience into channels.
- Positioning: how the blog is different and what it refuses to become.
- Style: voice, rhythm, metaphor boundaries, language, forbidden tone.
- Forbidden moves: claims, topics, tropes, or AI/internal jargon the blog must avoid.
- Author memory: notes with evidence/source context and tags.
- Editorial rules: active atomic rules for at least `author`, `audience`, and `goal`.
- Topics: editorial territories with purpose, audience value, author stance, rules, and forbidden angles.
- Fabulas: reusable story mechanics that can apply across multiple topics.
- Topic/fabula matrix: enabled combinations must not collapse into one-to-one pairs unless the blueprint explicitly says the project is intentionally narrow.
- Publication channels: destination mechanics only.
- Source signals: at least one realistic source signal for the first ready scenario.
- Ready scenarios: plan slot with source signal, topic, fabula, channel, expected value, and benchmark criteria.

## Canonical Ownership

- Publisher/editorial contract owns author, audience, goals, positioning, style, and forbidden moves.
- `PublicationChannel` owns platform, title/handle, language, role, publishing mode, status, and default size profile.
- `PublicationChannel.audience` is legacy data only. New fixtures must not set it.
- `EditorialModel.author/audience/goals` are compatibility summaries. UI-visible Publisher blocks and DraftRun context should be backed by `editorialRules`.
- Topic is the territory. Fabula is the reusable narrative mechanic.

## Safe Write Path

1. Update the blueprint document first and get approval when the concept is still changing.
2. Update UTF-8 source fixtures and docs.
3. Run fixture validation before refreshing backend state.
4. Refresh backend snapshots through application seed/reset or a dedicated safe script.
5. Verify UI/backend mode reads the refreshed project.

Do not patch Cyrillic content into SQLite with inline shell commands. If PowerShell output looks corrupted, re-read files with explicit UTF-8 handling before diagnosing the data.
