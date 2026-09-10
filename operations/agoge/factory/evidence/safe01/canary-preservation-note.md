## Post-acceptance preservation correction

Owner acceptance remains in force: #236 stays closed/accepted and Project Done. Its PASS is unchanged.

During the one authorized SAFE-01 service startup, Symphony's existing terminal-issue cleanup removed the now-closed GH-236 workspace instead of archiving it. This was detected during independent post-run preservation verification. The earlier acceptance comment's retained-workspace statement was no longer accurate after that cleanup.

The surviving original session transcript and committed host evidence allowed exact recovery: the original ten-file tree, parent, author, committer, timestamp and message reproduce **5cc507a336ee4146df0bcd4e2db45849cad2d924**, matching the original Git SHA. No new canary run or replacement evidence was used; no Git history was rewritten. The original probe and generated results were restored too.

Recovered original branch: symphony/GH-236-20260909T045317Z.
Durable checkout outside controller cleanup: /home/toluadmin/services/symphony/.factory-preservation/recovered-canary-236.
Full-history bundle: /home/toluadmin/services/symphony/.factory-preservation/accepted-canary-236.bundle. Git bundle verification and git fsck --full passed.

Factory local terminal cleanup has been corrected to archive the complete workspace by rename; archival failure leaves the source intact. A regression checks Git-object bytes, untracked evidence and failure preservation. This correction is installed with Symphony stopped/disabled. No additional #236 or #235 dispatch was performed.
