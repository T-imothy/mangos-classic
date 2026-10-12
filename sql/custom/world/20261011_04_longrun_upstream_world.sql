-- ManTech classic reviewed upstream and long-run fixes, 2026-10-11.
-- Matching WORLD database only. Back up affected tables before applying.

-- Item 19874's passive is equipped once, never re-applied on each hit.
UPDATE item_template SET spelltrigger_1=1 WHERE entry=19874 AND spellid_1=25669 AND spelltrigger_1=2;


-- Scene steps use native relay guards; parent cleanup must still run.
UPDATE dbscripts_on_relay SET priority=1 WHERE id=14 AND delay=2000 AND command=26 AND buddy_entry=4952 AND priority=0;
DELETE FROM dbscripts_on_relay WHERE id=14 AND delay=2000 AND command=48 AND priority=0;
INSERT INTO dbscripts_on_relay(`id`,`delay`,`priority`,`command`,`datalong`,`datalong2`,`datalong3`,`buddy_entry`,`search_radius`,`data_flags`,`dataint`,`dataint2`,`dataint3`,`dataint4`,`datafloat`,`x`,`y`,`z`,`o`,`speed`,`condition_id`,`comments`) VALUES('14','2000','0','48','512','0','0','0','0','4','0','0','0','0','0','0','0','0','0','0','0','ManTech training - remove own NPC immunity immediately before attack');
UPDATE dbscripts_on_relay SET datalong2=0 WHERE id=14 AND delay=35000 AND command=35 AND datalong=5 AND data_flags=4;
DELETE FROM dbscripts_on_relay WHERE id=1900014;
INSERT INTO dbscripts_on_relay(`id`,`delay`,`priority`,`command`,`datalong`,`datalong2`,`datalong3`,`buddy_entry`,`search_radius`,`data_flags`,`dataint`,`dataint2`,`dataint3`,`dataint4`,`datafloat`,`x`,`y`,`z`,`o`,`speed`,`condition_id`,`comments`) VALUES('1900014','0','0','31','4952','5','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','ManTech training - optional dummy cleanup guard');
INSERT INTO dbscripts_on_relay(`id`,`delay`,`priority`,`command`,`datalong`,`datalong2`,`datalong3`,`buddy_entry`,`search_radius`,`data_flags`,`dataint`,`dataint2`,`dataint3`,`dataint4`,`datafloat`,`x`,`y`,`z`,`o`,`speed`,`condition_id`,`comments`) VALUES('1900014','0','1','35','5','0','0','4952','5','1','0','0','0','0','0','0','0','0','0','0','0','ManTech training - reset only this dummy, never neighboring guards');
DELETE FROM dbscripts_on_relay WHERE id=14 AND delay=35000 AND command=45 AND datalong=1900014;
INSERT INTO dbscripts_on_relay(`id`,`delay`,`priority`,`command`,`datalong`,`datalong2`,`datalong3`,`buddy_entry`,`search_radius`,`data_flags`,`dataint`,`dataint2`,`dataint3`,`dataint4`,`datafloat`,`x`,`y`,`z`,`o`,`speed`,`condition_id`,`comments`) VALUES('14','35000','1','45','1900014','0','0','0','0','4','0','0','0','0','0','0','0','0','0','0','0','ManTech training - optional paired dummy cleanup');
