/* Classic AV discovery objectives. Released under GNU GPL v2 or later. */
#include "AI/ScriptDevAI/include/sc_common.h"
#include "BattleGround/BattleGround.h"

namespace
{
    struct npc_av_sky_lord_markerAI : public Scripted_NoMovementAI
    {
        explicit npc_av_sky_lord_markerAI(Creature* creature) : Scripted_NoMovementAI(creature) {}
        void Reset() override {}
        void UpdateAI(uint32) override {} // invisible discovery markers never attack.
        void MoveInLineOfSight(Unit* who) override
        {
            const uint32 entry = m_creature->GetEntry();
            if (entry < 14026 || entry > 14031 || !who || !who->IsPlayer()) return;
            Player* player = static_cast<Player*>(who);
            const uint32 quest = entry <= 14028 ? 7302 : 7301;
            const Team team = quest == 7302 ? HORDE : ALLIANCE;
            if (!player->IsInWorld() || !player->IsAlive() || player->IsBeingTeleported() ||
                !m_creature->IsInWorld() || !m_creature->IsAlive() || m_creature->GetMapId() != 30 || !player->IsInMap(m_creature) ||
                player->GetQuestStatus(quest) != QUEST_STATUS_INCOMPLETE || player->GetBGTeam() != team ||
                !player->IsWithinDistInMap(m_creature, INTERACTION_DISTANCE) || !player->IsWithinLOSInMap(m_creature)) return;
            BattleGround* bg = player->GetBattleGround();
            if (!bg || bg->GetTypeId() != BATTLEGROUND_AV || bg->GetStatus() != STATUS_IN_PROGRESS ||
                bg->GetBgMap() != player->GetMap() || !bg->GetPlayers().count(player->GetObjectGuid())) return;
            if (!player->GetReqKillOrCastCurrentCount(quest, entry))
                player->KilledMonsterCredit(entry, m_creature->GetObjectGuid());
        }
    };
}
void AddSC_av_quest_objectives()
{
    Script* script = new Script;
    script->Name = "npc_av_sky_lord_marker";
    script->GetAI = &GetNewAIInstance<npc_av_sky_lord_markerAI>;
    script->RegisterSelf();
}
