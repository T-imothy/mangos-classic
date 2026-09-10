/*
 * This file is part of the CMaNGOS Project. See AUTHORS file for Copyright information
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License, version 2 or later.
 */
#include "Chat/Chat.h"
#include "Chat/PlayerTravel.h"
#include "Chat/PlayerTravelDestinations.h"
#include "Config/Config.h"
#include "Database/DatabaseEnv.h"
#include "Entities/Player.h"
#include "Globals/ObjectMgr.h"
#include "Groups/Group.h"
#include "Maps/Map.h"
#include "Server/WorldSession.h"
#include "Server/DBCStores.h"
#include "World/World.h"

#include <chrono>

namespace
{
    PlayerTravel::Service travel;
    uint64_t manualSequence = 0;

    uint64_t TravelNow()
    {
        return std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();
    }

    const PlayerTravel::Destination* FindDestination(std::string key, bool aliases)
    {
        for (char& c : key)
            if (c >= 'A' && c <= 'Z')
                c += 'a' - 'A';
        // Canonical machine keys never resolve through an alias from another expansion.
        for (const auto& destination : PlayerTravel::Destinations)
            if (key == destination.key)
                return &destination;
        if (aliases)
            for (const auto& destination : PlayerTravel::Destinations)
            {
                if (PlayerTravel::Expansion < destination.firstExpansion ||
                    PlayerTravel::Expansion > destination.lastExpansion)
                    continue;
                std::istringstream names(destination.aliases);
                for (std::string name; names >> name;)
                    if (key == name)
                        return &destination;
            }
        return nullptr;
    }

    PlayerTravel::Position TravelPosition(Player* player)
    {
        PlayerTravel::Position position;
        position.inWorld = player->IsInWorld();
        position.transferring = player->IsBeingTeleported();
        position.alive = player->IsAlive();
        position.map = player->GetMapId();
        position.instance = player->GetInstanceId();
        position.x = player->GetPositionX();
        position.y = player->GetPositionY();
        position.z = player->GetPositionZ();
        return position;
    }

    std::string TravelEligibility(Player* player, const PlayerTravel::Destination* destination)
    {
        if (!sConfig.GetBoolDefault("PlayerTravel.Enabled", false))
            return "disabled";
        if (!player->IsInWorld() || player->IsBeingTeleported())
            return "transfer_busy";
#ifdef ENABLE_PLAYERBOTS
        if (!player->isRealPlayer())
            return "not_player";
#endif
        if (player->IsGameMaster())
            return "gm_mode"; // Native entry checks exempt GM mode; this command must not.
        if (!player->IsAlive())
            return "dead";
        if (player->IsInCombat())
            return "combat";
        if (player->IsTaxiFlying())
            return "taxi";
        if (player->GetTransport())
            return "transport";
        if (player->InBattleGround())
            return "battleground";
        if (!player->GetMap())
            return "transfer_busy";
        if (player->GetMap()->IsDungeon())
            return "instance";
        if (player->HasCharmer() || player->IsRooted() ||
            player->hasUnitState(UNIT_STAT_CAN_NOT_REACT_OR_LOST_CONTROL))
            return "controlled";
        if (Group* group = player->GetGroup())
            if (!group->IsLeader(player->GetObjectGuid()))
                return "not_leader";
        if (!destination || !destination->available)
            return "unavailable_destination";

        if (!player->LoadDungeonTravelUnlocks())
            return "storage_unavailable";
        if (!player->HasDungeonTravelUnlock(destination->key))
            return "undiscovered";

        const MapEntry* map = sMapStore.LookupEntry(destination->map);
        if (!map)
            return "unavailable_destination";
        const AreaTrigger* entry = destination->entryTrigger ?
            sObjectMgr.GetAreaTrigger(destination->entryTrigger) : nullptr;
        if (destination->entryTrigger && (!entry || entry->target_mapId != destination->instanceMap))
            return "unavailable_destination";
        if (entry && player->GetLevel() < entry->requiredLevel &&
            !sWorld.getConfig(CONFIG_BOOL_INSTANCE_IGNORE_LEVEL))
            return "too_low_level";

        if (map->IsDungeon())
        {
            if (!entry || entry->target_mapId != destination->map)
                return "unavailable_destination";
            uint32 requirement = 0;
            const AreaLockStatus status = player->GetAreaTriggerLockStatus(entry, requirement, true);
            switch (status)
            {
                case AREA_LOCKSTATUS_OK: break;
                case AREA_LOCKSTATUS_TOO_LOW_LEVEL: return "too_low_level";
                case AREA_LOCKSTATUS_RAID_LOCKED: return "raid_required";
                case AREA_LOCKSTATUS_ZONE_IN_COMBAT: return "instance_combat";
                case AREA_LOCKSTATUS_INSTANCE_IS_FULL: return "instance_full";
                case AREA_LOCKSTATUS_HAS_BIND: return "lockout";
                default: return "entry_requirements";
            }
        }
        return "";
    }

    bool StartTravel(Player* player, const PlayerTravel::Destination* destination)
    {
        if (!destination)
            return false;
        const AreaTrigger* entry = destination->map == destination->instanceMap ?
            sObjectMgr.GetAreaTrigger(destination->entryTrigger) : nullptr;
        // Only the requesting session's player moves. Preserve native transfer/entry checks.
        return player->TeleportTo(destination->map, destination->x, destination->y,
            destination->z, destination->orientation, 0, entry);
    }
}

bool ChatHandler::HandlePlayerTravelCommand(char* args)
{
    if (!m_session || !m_session->GetPlayer())
        return false;
    Player* player = m_session->GetPlayer();
    std::istringstream input(args ? args : "");
    std::vector<std::string> words;
    for (std::string word; input >> word;)
    {
        words.push_back(word);
        if (words.size() > 4)
            break;
    }
    const uint64_t now = TravelNow();
    const PlayerTravel::Service::Owner owner(m_session->GetAccountId(), player->GetGUIDLow());
    const bool machine = !words.empty() && words[0].size() >= 2 &&
        words[0][0] == 'v' && words[0][1] >= '0' && words[0][1] <= '9';
    const std::string id = machine && words.size() > 1 ? words[1] : "invalid";
    const std::string key = machine && words.size() > 3 ? words[3] : "invalid";
    auto send = [&](PlayerTravel::Reply reply)
    {
        SendSysMessage(reply.Line(id, key).c_str());
    };
    if (!travel.AllowRequest(owner, now))
    {
        if (machine)
            send({"denied", "rate_limit"});
        else
            SendSysMessage("Travel: too many requests. Try again shortly.");
        return true;
    }
    if (machine && words.size() == 4 && words[0] == "v1" &&
        words[2] == "unlocks" && key == "all" && PlayerTravel::Token(id, 64))
    {
        if (!sConfig.GetBoolDefault("PlayerTravel.Enabled", false))
            send({"denied", "disabled"});
        else if (!travel.AllowCatalog(owner, now))
            send({"denied", "rate_limit"});
        else if (!player->LoadDungeonTravelUnlocks())
            send({"denied", "storage_unavailable"});
        else
        {
            unsigned count = 0;
            for (const auto& destination : PlayerTravel::Destinations)
                if (destination.available)
                    ++count;
            const std::string prefix = "PBTPU 1 " + id + " ";
            SendSysMessage((prefix + "begin " + std::to_string(count)).c_str());
            for (const auto& destination : PlayerTravel::Destinations)
                if (destination.available)
                    SendSysMessage((prefix + destination.key +
                        (player->HasDungeonTravelUnlock(destination.key) ? " unlocked" : " locked")).c_str());
            SendSysMessage((prefix + "end " + std::to_string(count)).c_str());
        }
        return true;
    }
    if (machine)
    {
        if (words[0] != "v1")
            send({"unsupported", "version"});
        else if (words.size() != 4 || !PlayerTravel::Token(id, 64) || !PlayerTravel::Token(key, 48))
            send({"denied", "arguments"});
        else
        {
            const auto* destination = FindDestination(key, false);
            send(travel.Process(owner, id, words[2], key, destination, PlayerTravel::Expansion,
                TravelPosition(player), TravelEligibility(player, destination),
                std::max(0, sConfig.GetIntDefault("PlayerTravel.CooldownSeconds", 300)), now,
                [&]() { return StartTravel(player, destination); }));
        }
        return true;
    }
    if (words.empty())
    {
        if (!player->LoadDungeonTravelUnlocks())
        {
            SendSysMessage("Travel: unlock history is unavailable. Contact the server administrator.");
            return true;
        }
        SendSysMessage("Usage: .tp <destination> (for example .tp SM or .tp Ulda). Available destinations:");
        for (const auto& destination : PlayerTravel::Destinations)
            if (destination.available)
            {
                const std::string line = std::string(destination.name) + ": .tp " + destination.key +
                    " (" + destination.aliases + ") [" +
                    (player->HasDungeonTravelUnlock(destination.key) ? "unlocked" : "locked: enter this dungeon first") + "]";
                SendSysMessage(line.c_str());
            }
        return true;
    }
    const auto* destination = words.size() == 1 && PlayerTravel::Token(words[0], 48) ?
        FindDestination(words[0], true) : nullptr;
    if (!destination)
    {
        SendSysMessage("Travel: invalid destination. Use .tp to list destinations.");
        return true;
    }
    const std::string request = "manual_" + std::to_string(++manualSequence);
    auto process = [&](const char* operation)
    {
        return travel.Process(owner, request, operation, destination->key, destination,
            PlayerTravel::Expansion, TravelPosition(player), TravelEligibility(player, destination),
            std::max(0, sConfig.GetIntDefault("PlayerTravel.CooldownSeconds", 300)), now,
            [&]() { return StartTravel(player, destination); });
    };
    auto reply = process("check");
    if (reply.state == "ready")
        reply = process("go");
    if (reply.reason == "undiscovered")
    {
        SendSysMessage("Travel locked: enter this dungeon once to unlock its teleport for this character.");
        return true;
    }
    const std::string line = reply.state == "pending" ? std::string("Travelling to ") + destination->name + "." :
        "Travel denied: " + reply.reason + ".";
    SendSysMessage(line.c_str());
    return true;
}

// Load lazily for human visitors/requests, not every random bot at startup.
bool Player::LoadDungeonTravelUnlocks()
{
    if (m_dungeonTravelUnlocksLoaded)
        return true;
    // A sentinel guarantees a row for an empty history; query failure stays fail-closed.
    auto result = CharacterDatabase.PQuery(
        "SELECT destination FROM character_dungeon_travel WHERE guid = %u UNION ALL SELECT ''", GetGUIDLow());
    if (!result)
        return false;
    do
    {
        const std::string key = result->Fetch()[0].GetString();
        const auto* destination = FindDestination(key, false);
        if (destination && destination->available)
            m_dungeonTravelUnlocks.insert(destination->key);
    }
    while (result->NextRow());
    m_dungeonTravelUnlocksLoaded = true;
    return true;
}

void Player::RecordDungeonTravelVisit()
{
    if (!sConfig.GetBoolDefault("PlayerTravel.Enabled", false) || !IsInWorld() || !IsAlive() ||
        IsGameMaster() || !GetMap() || !GetMap()->IsDungeon())
        return;
#ifdef ENABLE_PLAYERBOTS
    if (!isRealPlayer())
        return;
#endif
    bool supported = false;
    for (const auto& destination : PlayerTravel::Destinations)
        if (destination.available && destination.instanceMap == GetMapId())
            supported = true;
    if (!supported || !LoadDungeonTravelUnlocks())
        return;
    std::vector<const char*> discovered;
    std::ostringstream query;
    query << "INSERT IGNORE INTO character_dungeon_travel (guid, destination, first_visit) VALUES ";
    for (const auto& destination : PlayerTravel::Destinations)
        if (destination.available && destination.instanceMap == GetMapId() &&
            !HasDungeonTravelUnlock(destination.key))
        {
            if (!discovered.empty())
                query << ',';
            // Both the numeric GUID and canonical whitelist key are server-owned values.
            query << '(' << GetGUIDLow() << ",'" << destination.key << "',UNIX_TIMESTAMP())";
            discovered.push_back(destination.key);
        }
    // One bounded insert on first entry only; publish the in-memory unlock after persistence succeeds.
    if (!discovered.empty() && CharacterDatabase.DirectExecute(query.str().c_str()))
        for (const char* key : discovered)
            m_dungeonTravelUnlocks.insert(key);
}
