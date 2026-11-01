-- Classic: bind only Loatheb's four class-specific Corrupted Mind proc auras.
INSERT INTO spell_scripts (Id, ScriptName) VALUES
(29185,'spell_loatheb_corrupted_mind_cooldown'),
(29194,'spell_loatheb_corrupted_mind_cooldown'),
(29196,'spell_loatheb_corrupted_mind_cooldown'),
(29198,'spell_loatheb_corrupted_mind_cooldown')
ON DUPLICATE KEY UPDATE ScriptName=VALUES(ScriptName);
