-- Targeted production log repairs; idempotent and expansion-specific.
-- Repair the obsolete trigger name without replacing other bindings.
UPDATE scripted_areatrigger SET ScriptName='at_southwind_tower'
WHERE entry=3146 AND ScriptName='at_hive_tower';

-- Restore the referenced Dune Smasher path/spawn from the Classic seed.
INSERT INTO creature (`guid`,`id`,`map`,`position_x`,`position_y`,`position_z`,`orientation`,`spawntimesecsmin`,`spawntimesecsmax`,`spawndist`,`MovementType`) SELECT 23120,5469,1,-9538.48,-2779.92,7.96304,2.25491,600,600,0,2 WHERE NOT EXISTS (SELECT 1 FROM creature WHERE guid=23120) AND EXISTS (SELECT 1 FROM creature_template WHERE Entry=5469);
-- The converted native spell list must identify its main ranged spell.
UPDATE creature_spell_list SET Flags=Flags|2
WHERE Id=429301 AND Position=4 AND SpellId=9613 AND Flags=0;
