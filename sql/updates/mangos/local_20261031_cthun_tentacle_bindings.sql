-- Classic: restore bindings required by the existing native tentacle scripts.
-- Apply only after checking for conflicting bindings; do not reload spell
-- scripts on an older running executable as part of deployment.
INSERT INTO spell_scripts (Id, ScriptName) VALUES
(26586,'spell_birth_tentacles'),
(26140,'spell_summon_hook_tentacle'),
(26216,'spell_summon_giant_hook_tentacles'),
(26150,'spell_summon_eye_tentacle'),
(26768,'spell_summon_giant_eye_tentacles')
ON DUPLICATE KEY UPDATE ScriptName=VALUES(ScriptName);
