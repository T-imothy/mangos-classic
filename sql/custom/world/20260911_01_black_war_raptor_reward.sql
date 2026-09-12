-- ManTech level-40 player reward. Preserve item/spell IDs across expansions.
-- Run with the matching core release: spell 22721 scales to 60/100% server-side.
UPDATE item_template
SET AllowableRace=-1, RequiredLevel=40, RequiredSkill=762, RequiredSkillRank=75,
    requiredhonorrank=0, RequiredCityRank=0, RequiredReputationFaction=0, RequiredReputationRank=0
WHERE entry=18246;
