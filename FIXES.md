# Fix crash when making a new Clan, plus a few other crashes

Making a new Clan crashed on the symbol screen with `NameError: name 'clan' is not defined`
(in generate_lead_ceremony) so clan.json never got written and the game then showed
"There was an error loading the clan.json" on the next start. Was messing around with it and while testing the fix I found a few more crashes, so this SHOULD fix those too

### Fixes
- New Clan crash: generate_lead_ceremony used `clan` without it being set. Now it takes
  the Clan as a parameter or uses the leader's own Clan if nothing is given. create_clan and
  new_leader and the leader ceremony pass their Clan in

- Leader dying from an illness, injury or permanent condition: the same missing `clan`
  in moon_skip_illness, moon_skip_injury and moon_skip_permanent_condition. The life now
  comes off the leader's own Clan.

- Other Clans' new leaders got the old leader's lives: new_leader ran the ceremony before
  reset_leader_lives. The lives are done first now, so the same order as _handle_leader_ceremony.

- First moon crash: OtherClan had no game_mode which is what get_amount_cat_for_one_medic
  reads during the apprentice ceremony. Other Clans now follow the player Clan's game mode.

- Cross-Clan injury events: handle_injury used `main_cat` instead of `self.main_cat`.

- Crash when cats die (KeyError on a Clan prefix): the block that adds the deaths event
  was outside the loop so it only ran for the last Clan and crashed when that
  Clan had no deaths. It is inside the loop now so each Clan gets its own event. I also removed
  a fetch_clan_object() call that was missing its argument and the `return` that ended the
  whole moon early when a Clan had nobody left alive to be shaken.
