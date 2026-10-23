-- ManTech Classic only: allow a full 40-player raid in Blackrock Spire.
-- Upper and Lower Blackrock Spire share map 229 and its instance-wide cap.
-- Apply to the Classic world database; restart the world server to reload
-- the cached instance template. No binary rebuild is required.
UPDATE `instance_template` SET `maxPlayers` = 40 WHERE `map` = 229;
