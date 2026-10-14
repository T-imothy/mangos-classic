/* Classic AV stable quests. Released under GNU GPL v2 or later. */
#include "AI/ScriptDevAI/include/sc_common.h"
#include "AI/EventAI/CreatureEventAI.h"
#include "BattleGround/BattleGroundAV.h"
#include "MotionGenerators/MotionMaster.h"

namespace
{
    bool AvStableReady(Player* player, Creature* beast, uint32 quest)
    {
        if (!player || !beast || !player->IsInWorld() || !player->IsAlive() || player->IsBeingTeleported() ||
            !beast->IsInWorld() || !beast->IsAlive() || beast->HasCharmer() || beast->GetMapId() != 30 ||
            !player->IsInMap(beast) || player->GetQuestStatus(quest) != QUEST_STATUS_INCOMPLETE) return false;
        BattleGround* bg = player->GetBattleGround();
        return bg && bg->GetTypeId() == BATTLEGROUND_AV && bg->GetStatus() == STATUS_IN_PROGRESS &&
            bg->GetBgMap() == player->GetMap() &&
            bg->GetPlayers().count(player->GetObjectGuid()) &&
            player->GetBGTeam() == (quest == 7001 ? HORDE : ALLIANCE);
    }
    struct av_stable_beastAI : public CreatureEventAI
    {
        explicit av_stable_beastAI(Creature* creature) : CreatureEventAI(creature), originalFaction(creature->GetFaction()) {}
        ObjectGuid owner;
        uint32 originalFaction;
        uint32 checkTimer = 0;
        bool delivered = false;
        uint32 QuestId() const { return m_creature->GetEntry() == 10981 ? 7001 : 7027; }
        uint32 TameSpell() const { return m_creature->GetEntry() == 10981 ? 21794 : 21866; }
        void JustRespawned() override
        {
            owner.Clear(); delivered = false; checkTimer = 0;
            m_creature->setFaction(originalFaction);
            CreatureEventAI::JustRespawned();
        }
        void SpellHit(Unit* caster, const SpellEntry* spell) override
        {
            CreatureEventAI::SpellHit(caster, spell); // retain the original wild charge/rend events.
            if (delivered || !caster || !caster->IsPlayer() || !spell || spell->Id != TameSpell() ||
                (m_creature->GetEntry() != 10981 && m_creature->GetEntry() != 10990)) return;
            Player* player = static_cast<Player*>(caster);
            if (!AvStableReady(player, m_creature, QuestId()) ||
                (!owner.IsEmpty() && owner != player->GetObjectGuid()) ||
                !m_creature->GetSpellAuraHolder(TameSpell(), player->GetObjectGuid())) return;
            if (!owner.IsEmpty()) return; // repeated aura/cast does not restart the route.
            owner = player->GetObjectGuid(); checkTimer = 0;
            m_creature->CombatStop(true);
            m_creature->DeleteThreatList();
            m_creature->setFaction(player->GetFaction());
            m_creature->GetMotionMaster()->MoveFollow(player, 2.0f, M_PI_F);
        }
        void UpdateAI(uint32 diff) override
        {
            if (owner.IsEmpty()) { CreatureEventAI::UpdateAI(diff); return; }
            if (delivered) return;
            if (checkTimer > diff) { checkTimer -= diff; return; }
            checkTimer = 500;
            Player* player = m_creature->GetMap()->GetPlayer(owner);
            if (!AvStableReady(player, m_creature, QuestId()) ||
                !m_creature->GetSpellAuraHolder(TameSpell(), owner))
            {
                owner.Clear(); m_creature->RemoveAurasDueToSpell(TameSpell());
                m_creature->setFaction(originalFaction);
                CreatureEventAI::EnterEvadeMode();
                return;
            }
            if (m_creature->IsInCombat()) { CreatureEventAI::UpdateAI(diff); return; }
            if (m_creature->GetMotionMaster()->GetCurrentMovementGeneratorType() != FOLLOW_MOTION_TYPE)
                m_creature->GetMotionMaster()->MoveFollow(player, 2.0f, M_PI_F);
        }
        bool Deliver(Player* player, Creature* stable)
        {
            const uint32 expected = QuestId() == 7001 ? 13616 : 13617;
            if (delivered || !player || owner != player->GetObjectGuid() || !AvStableReady(player, m_creature, QuestId()) ||
                !m_creature->GetSpellAuraHolder(TameSpell(), owner) ||
                !stable || stable->GetEntry() != expected || !stable->IsAlive() || !m_creature->IsInMap(stable) ||
                m_creature->IsInCombat() || !m_creature->IsWithinDistInMap(stable, 5.0f) ||
                !m_creature->IsWithinLOSInMap(stable) || !player->IsWithinDistInMap(stable, 5.0f)) return false;
            delivered = true;
            player->AreaExploredOrEventHappens(QuestId()); // event credit only; native reward/turn-in remains required.
            m_creature->GetMotionMaster()->MoveIdle();
            m_creature->ForcedDespawn(1000);
            return true;
        }
    };
    bool GossipHello_av_stable_master(Player* player, Creature* stable)
    {
        if (stable->GetMapId() == 30 && player->IsInWorld() && !player->IsBeingTeleported() && player->IsInMap(stable))
        {
            const uint32 beastEntry = stable->GetEntry() == 13616 ? 10981 : 10990;
            CreatureList beasts;
            GetCreatureListWithEntryInGrid(beasts, stable, beastEntry, 5.0f);
            for (Creature* beast : beasts)
                if (auto* ai = dynamic_cast<av_stable_beastAI*>(beast->AI()))
                    if (ai->Deliver(player, stable)) break;
        }
        // Let the native handler build the quest/stable menu after credit.
        return false;
    }
}
void AddSC_av_stable_quests()
{
    Script* script = new Script;
    script->Name = "npc_av_stable_beast";
    script->GetAI = [](Creature* creature) -> CreatureAI* { return new av_stable_beastAI(creature); };
    script->RegisterSelf();
    script = new Script;
    script->Name = "npc_av_stable_master";
    script->pGossipHello = &GossipHello_av_stable_master;
    script->RegisterSelf();
}
