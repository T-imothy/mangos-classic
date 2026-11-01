-- Classic local candidate; not deployed to production.
-- These exact native spell-targeted wall spawns must run npc_invible_man,
-- which schedules Summon Web Wrap (28627) after the player's pull finishes.
-- Generic World Trigger (15384) has no AI and leaves no attackable rescue web.
-- Retain coordinates/GUIDs; never change the generic World Trigger template.
UPDATE creature c
JOIN spell_script_target t ON t.type=3 AND t.targetEntry=c.guid
SET c.id=17286
WHERE c.map=533 AND c.id=15384 AND
 ((t.entry=29280 AND c.guid=5331295) OR (t.entry=29281 AND c.guid=5331297) OR
  (t.entry=29282 AND c.guid=5331298) OR (t.entry=29283 AND c.guid=5331299) OR
  (t.entry=29285 AND c.guid=5331300) OR (t.entry=29287 AND c.guid=5331301));
