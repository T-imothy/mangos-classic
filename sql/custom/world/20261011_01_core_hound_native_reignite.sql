-- Apply ONLY to the matching world DB after deploying the accompanying core.
-- Restore native Core Hound collapse/reignite; keep EventAI Serrated Bite.
-- Preserve any independently installed alternative AI binding.
UPDATE creature_template
SET ScriptName = 'npc_core_hound'
WHERE Entry = 11671 AND AIName = 'EventAI' AND ScriptName IN ('', 'npc_core_hound');
SELECT Entry, Name, AIName, ScriptName FROM creature_template WHERE Entry = 11671;
