/* Classic AV commander rescues. Released under GNU GPL v2 or later.
 * Return routes: VMaNGOS db-4641790; see doc/av-commander-rescues.txt. */
#include "AI/ScriptDevAI/include/sc_common.h"
#include "AI/EventAI/CreatureEventAI.h"
#include "BattleGround/BattleGround.h"
#include "MotionGenerators/MotionMaster.h"
#include "MotionGenerators/WaypointManager.h"

namespace
{
    struct AvCommander
    {
        uint32 entry, marker, quest, path, lastPoint;
        Team team;
    };
    AvCommander const commanders[] =
    {
        {13179, 14026, 7302, 613179, 75, HORDE},
        {13180, 14028, 7302, 613180, 85, HORDE},
        {13181, 14027, 7302, 613181, 98, HORDE},
        {13437, 14029, 7301, 613437, 93, ALLIANCE},
        {13438, 14030, 7301, 613438, 67, ALLIANCE},
        {13439, 14031, 7301, 613439, 77, ALLIANCE},
    };
    AvCommander const* CommanderData(uint32 entry)
    {
        for (auto const& data : commanders) if (data.entry == entry) return &data;
        return nullptr;
    }
    bool CommanderVisitor(Player* player, Creature* creature, AvCommander const* data)
    {
        if (!player || !creature || !data || !player->IsInWorld() || !player->IsAlive() || player->IsBeingTeleported() ||
            !creature->IsInWorld() || !creature->IsAlive() || creature->GetMapId() != 30 ||
            !player->IsInMap(creature) || player->GetBGTeam() != data->team ||
            !player->IsWithinDistInMap(creature, INTERACTION_DISTANCE) || !player->IsWithinLOSInMap(creature)) return false;
        BattleGround* bg = player->GetBattleGround();
        return bg && bg->GetTypeId() == BATTLEGROUND_AV && bg->GetStatus() == STATUS_IN_PROGRESS &&
            bg->GetBgMap() == player->GetMap() && bg->GetPlayers().count(player->GetObjectGuid());
    }
    struct npc_av_wing_commanderAI : public CreatureEventAI
    {
        explicit npc_av_wing_commanderAI(Creature* creature) : CreatureEventAI(creature),
            data(CommanderData(creature->GetEntry())), prison(creature->GetRespawnPosition()),
            originalMovement(creature->GetDefaultMovementType()), originalFlags(creature->GetUInt32Value(UNIT_NPC_FLAGS)) {}
        AvCommander const* data;
        Position prison;
        MovementGeneratorType originalMovement;
        uint32 originalFlags, nextPoint = 1;
        bool returning = false, arrived = false, finishPending = false, resumePending = false;

        WaypointPath const* ReturnPath() const
        {
            if (!data) return nullptr;
            auto* path = sWaypointMgr.GetPathFromOrigin(data->entry, m_creature->GetGUIDLow(), data->path, PATH_FROM_WAYPOINT_PATH);
            if (!path || path->size() != data->lastPoint || path->begin()->first != 1 || path->rbegin()->first != data->lastPoint)
                return nullptr;
            return path;
        }
        uint32 GetCurrentWaypointPath() const override { return data ? data->path : 0; }
        void Discover(Player* player)
        {
            // Discovery belongs to the prisoner location, not the returned NPC at base.
            if (returning || arrived || !CommanderVisitor(player, m_creature, data)) return;
            if (player->GetQuestStatus(data->quest) == QUEST_STATUS_INCOMPLETE &&
                !player->GetReqKillOrCastCurrentCount(data->quest, data->marker))
                player->KilledMonsterCredit(data->marker, m_creature->GetObjectGuid());
        }
        void MoveInLineOfSight(Unit* who) override
        {
            if (who && who->IsPlayer()) Discover(static_cast<Player*>(who));
            CreatureEventAI::MoveInLineOfSight(who);
        }
        void ContinueReturn()
        {
            if (!ReturnPath()) return;
            m_creature->SetWalk(false);
            m_creature->GetMotionMaster()->Clear(false, true);
            m_creature->GetMotionMaster()->MoveWaypoint(data->path, PATH_FROM_WAYPOINT_PATH, 0, 0, FORCED_MOVEMENT_RUN);
            m_creature->GetMotionMaster()->SetNextWaypoint(nextPoint);
            resumePending = false;
        }
        bool Rescue(Player* player)
        {
            if (returning || arrived || !CommanderVisitor(player, m_creature, data) || m_creature->IsInCombat() || !ReturnPath()) return false;
            Discover(player);
            returning = true; nextPoint = 1;
            m_creature->SetUInt32Value(UNIT_NPC_FLAGS, UNIT_NPC_FLAG_NONE);
            m_creature->SetStandState(UNIT_STAND_STATE_STAND);
            m_creature->RemoveAurasDueToSpell(16380);
            ContinueReturn();
            return true;
        }
        void MovementInform(uint32 type, uint32 point) override
        {
            CreatureEventAI::MovementInform(type, point);
            if (!returning || !data || type != EXTERNAL_WAYPOINT_MOVE || point != nextPoint) return;
            auto* path = ReturnPath();
            if (!path) return;
            auto node = path->find(point);
            if (node == path->end()) return;
            // Native evade returns to the last safe checkpoint, then resumes the route.
            m_creature->SetRespawnCoord(node->second.x, node->second.y, node->second.z, m_creature->GetOrientation());
            ++nextPoint;
            if (point == data->lastPoint) finishPending = true;
        }
        void JustReachedHome() override
        {
            CreatureEventAI::JustReachedHome();
            if (returning && !finishPending) resumePending = true;
        }
        bool ProcessAction(CreatureEventAI_Action const& action, uint32 rnd, uint32 eventId,
            Unit* invoker, Unit* sender, Unit* target) override
        {
            // Keep Ichman's existing combat kit without re-hiding the rescued NPC.
            if ((returning || arrived) && data && data->entry == 13437 &&
                action.type == ACTION_T_CAST && action.cast.spellId == 16380) return true;
            return CreatureEventAI::ProcessAction(action, rnd, eventId, invoker, sender, target);
        }
        void UpdateAI(uint32 diff) override
        {
            CreatureEventAI::UpdateAI(diff);
            if (!returning || !m_creature->IsAlive() || m_creature->IsInCombat() || GetAIOrder() == ORDER_EVADE) return;
            if (finishPending)
            {
                // Change generators outside their MovementInform callback.
                returning = false; arrived = true; finishPending = resumePending = false;
                m_creature->SetDefaultMovementType(IDLE_MOTION_TYPE);
                m_creature->GetMotionMaster()->Clear(false, true);
                m_creature->GetMotionMaster()->MoveIdle();
                m_creature->SetUInt32Value(UNIT_NPC_FLAGS, (originalFlags | UNIT_NPC_FLAG_QUESTGIVER) & ~UNIT_NPC_FLAG_GOSSIP);
            }
            else if (resumePending) ContinueReturn();
        }
        void JustRespawned() override
        {
            returning = arrived = finishPending = resumePending = false; nextPoint = 1;
            m_creature->SetRespawnCoord(prison.x, prison.y, prison.z, prison.o);
            m_creature->SetDefaultMovementType(originalMovement);
            m_creature->SetUInt32Value(UNIT_NPC_FLAGS, originalFlags);
            CreatureEventAI::JustRespawned();
        }
        void JustDied(Unit* killer) override
        {
            // Native respawn must use the prisoner spawn, not a return checkpoint.
            returning = arrived = finishPending = resumePending = false; nextPoint = 1;
            m_creature->SetRespawnCoord(prison.x, prison.y, prison.z, prison.o);
            m_creature->SetDefaultMovementType(originalMovement);
            CreatureEventAI::JustDied(killer);
        }
    };
    bool GossipHello_av_wing_commander(Player* player, Creature* creature)
    {
        auto* ai = dynamic_cast<npc_av_wing_commanderAI*>(creature->AI());
        if (!ai || ai->returning || ai->arrived || !CommanderVisitor(player, creature, ai->data)) return false;
        ai->Discover(player);
        player->PrepareQuestMenu(creature->GetObjectGuid());
        if (!creature->IsInCombat() && ai->ReturnPath())
            player->ADD_GOSSIP_ITEM(GOSSIP_ICON_CHAT, "I have your back. Return to our base!", GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 1);
        player->SEND_GOSSIP_MENU(player->GetGossipTextId(creature), creature->GetObjectGuid());
        return true;
    }
    bool GossipSelect_av_wing_commander(Player* player, Creature* creature, uint32 sender, uint32 action)
    {
        player->CLOSE_GOSSIP_MENU();
        if (sender == GOSSIP_SENDER_MAIN && action == GOSSIP_ACTION_INFO_DEF + 1)
            if (auto* ai = dynamic_cast<npc_av_wing_commanderAI*>(creature->AI())) ai->Rescue(player);
        return true;
    }
}
void AddSC_av_wing_commanders()
{
    Script* script = new Script;
    script->Name = "npc_av_wing_commander";
    script->GetAI = &GetNewAIInstance<npc_av_wing_commanderAI>;
    script->pGossipHello = &GossipHello_av_wing_commander;
    script->pGossipSelect = &GossipSelect_av_wing_commander;
    script->RegisterSelf();
}
