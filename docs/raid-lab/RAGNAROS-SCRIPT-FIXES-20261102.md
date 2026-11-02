# Ragnaros script fixes: verified defects, not encounter acceptance

The user paused raid progression testing and then clarified on 2026-11-02 that the verified fixes should be published through the existing Classic live release. This source note does not establish deployment; the coordinated release receipt records the installed binary and restart status.

## Changes

- Keep the boss stationary with the AI-owned immobilization state. Removing a temporary root must not clear the encounter's stationary state and make Ragnaros chase a new victim.
- Process each native summoned creature GUID once. The native wild-summon callbacks could notify twice, counting sixteen Sons instead of eight and casting each Flame's Intense Heat twice.
- Call the base combat-AI death handler before recording encounter completion.

## Evidence

The actual-body C++ root regression reproduced the defect before the fix and passed afterward. The phase regression reproduced duplicate summon processing before the fix and passed afterward, including eight Sons, one heat cast per Flame, old-wave death isolation and the final-Son timer transition. The native trace `raid-50344609-409-4` recorded eight Flame actors with one Intense Heat cast each.

The complete Classic laboratory candidate compiled successfully on 2026-11-02 at 06:08:44 Chicago time. Its executable SHA256 is `0129067cda324be8cc4712a6e75d71b46f89b21b2be351537aba3ee385fea100`. That build also contained unfinished playerbot changes; it is not a production release of this isolated commit.

From a configured C++ compiler environment, run:

```text
python tests/ragnaros_root_regression.py .
python tests/ragnaros_phase_regression.py .
```

These checks do not certify the entire fight. Native bot raids still fail; knockback recovery, damage uptime and raid survival need further work. Killing all eight Sons and observing early emergence still needs a complete native acceptance run. The unfinished laboratory work is preserved locally; the temporary publication branches were removed at the user's request. This release retains the existing production playerbots pin and excludes the experimental raid behavior changes. Automated raid testing remains paused.
