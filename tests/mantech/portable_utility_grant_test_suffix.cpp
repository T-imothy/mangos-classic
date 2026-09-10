int main() {
    ObjectGuid guid(HIGHGUID_PLAYER,1);Player player;
    auto grant=[&]{return ManTechPortableUtilityGrant::GrantToCharacter(guid,&player);};
    fixture={};assert(grant());assert((fixture.sent==std::vector<uint32>{65000,65001,65002}));
    assert(!grant());assert(fixture.sent.size()==3);
    fixture={};fixture.grants={"portable_utilities_v1"};assert(grant());assert((fixture.sent==std::vector<uint32>{65002}));
    fixture={};fixture.grants={"portable_mailbox_v1","portable_repair_v1"};assert(grant());assert((fixture.sent==std::vector<uint32>{65002}));
    // Transfers with every combination of bag/bank, pending-mail and unsaved online ownership.
    for(unsigned mask=0;mask<8;++mask)for(unsigned storage=0;storage<3;++storage){
        fixture={};std::vector<uint32> expected;
        for(unsigned i=0;i<3;++i){auto id=65000u+i;
            if(mask&(1u<<i)){
                if(storage==0)fixture.inventory.insert(id);
                if(storage==1)fixture.mail.insert(id);
                if(storage==2)fixture.unsaved.insert(id);
            }else expected.push_back(id);
        }
        grant();assert(fixture.sent==expected);assert(fixture.grants.size()==3);
        // Once recognized as owned, removing an item does not create another one-time gift.
        fixture.inventory.clear();fixture.mail.clear();fixture.unsaved.clear();
        assert(!grant());assert(fixture.sent==expected);
    }
    fixture={};fixture.bot=true;assert(!grant());assert(fixture.sent.empty());
    fixture={};fixture.eligible=false;assert(!grant());assert(fixture.sent.empty());
    fixture={};fixture.failedRead=true;assert(!grant());assert(fixture.sent.empty());assert(fixture.grants.empty());
    fixture={};player.id=2;assert(!grant());assert(fixture.sent.empty());
    std::cout<<"PASS actual grant implementation: fresh, legacy, copied, partial, bank/mail/unsaved, repeat, bot, deleted, failed-read and wrong-player cases\n";
}
