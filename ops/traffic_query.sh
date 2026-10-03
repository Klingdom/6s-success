#!/bin/sh
# Read real traffic straight from Umami's database. Runs ON THE VPS.
#
# The API returned 401 because the stored token expired, and there is no Umami
# password anywhere in our secrets to mint a new one. Resetting the admin
# password would restore API access and risk locking Phil out of the UI, so
# this reads the database instead: no credential changes, nothing written.
#
# Shipped as a file rather than an inlined ssh command because the quoting of a
# UUID inside psql inside ssh inside a shell mangled the query into an empty
# identifier twice.
#
# docker exec needs -i here. Without it the container gets no stdin, psql
# reads nothing, and every query returns silently empty, which looks exactly
# like a site with no traffic.
#
# TWO SCHEMA FACTS THAT COST A FORTNIGHT, WRITTEN DOWN SO THEY DO NOT AGAIN
# ------------------------------------------------------------------------
# 1. website_event's primary key is `event_id`. There is no `id` column and no
#    `website_event_id` column on it; `website_event_id` is the FOREIGN key,
#    over on event_data. So the join is
#
#        event_data.website_event_id = website_event.event_id
#
#    Joining the other way round is not an error, it is an empty result, and an
#    empty result here reads as "the site sends no event payloads". That is why
#    EXP-002 sat marked blocked while its data was sitting in the table all
#    along: eleven scroll-depth events, each with both of its properties.
#
# 2. website_event.session_id is the VISITOR, not the visit. Umami hashes it
#    per person and it persists across days: one session_id here spans
#    2026-08-21 to 2026-08-28. The visit is `visit_id`, and there are far more
#    of them. Anything that reports count(distinct session_id) under the word
#    "sessions" is reporting visitors and understating visits by about 3x.
set -e
# NOT WRITTEN WITH LIKE, AND THIS IS THE SECOND VERSION OF THIS BLOCK.
#
# The first used `not like '/__%'`, which is wrong in a way that reads as
# correct: in SQL LIKE, _ is a single-character wildcard, so that pattern
# excluded every path of three or more characters. Running it reported 117
# all-time pageviews and 52 visitors against a known baseline of 1,047 and 96,
# and `top pages` listed exactly one row. It would have quietly deleted most of
# the site's measured traffic from every figure this file produces, which is a
# worse failure than the single synthetic row it was written to hide.
#
# starts_with() has no wildcard semantics at all. Caught only because the
# output was compared against GOALS.md's own baseline instead of being read for
# plausibility; 117 is a perfectly plausible-looking number.
# A RESERVED PATH PREFIX, SO A LIVE PROBE CANNOT BECOME A VISITOR
# ----------------------------------------------------------------
# Every query below excludes url_path starting with /__ .
#
# Written 2026-10-03, the same hour it was needed. Verifying the new
# headless-beacon guard in site/nginx/default.conf meant POSTing a real beacon
# from a real browser user agent, because nothing short of that proves the
# guard lets a visitor through. That POST was recorded, correctly, as one
# pageview and one visitor on /__guard_probe: a synthetic arrival inside the
# one metric every objective in GOALS.md is measured against, created by the
# very check that existed to protect it.
#
# The raw row is deliberately NOT deleted. Raw measurement is the thing you
# never edit, and a reader who wants to know what the server actually received
# should be able to find it. Excluding it here is honest and it generalises:
# any future live probe named /__something is handled before it is made.
#
# So the rule for any session verifying something against live analytics: send
# it to a path beginning /__ . Nothing on this site serves one, nothing links
# to one, and nothing counts one.
C=umami-analytics-vi0p-umami-db-1
W=f1fc5160-4473-422d-a89e-73ff6cbdca7a

echo "== 6s-success.com (visitors = distinct session_id, visits = visit_id) =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select 'all_time',
       count(*) filter (where event_type = 1) as pageviews,
       count(distinct session_id) as visitors,
       count(distinct visit_id) as visits,
       to_char(min(created_at), 'YYYY-MM-DD'),
       to_char(max(created_at), 'YYYY-MM-DD')
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__');

select 'last_30d',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
       count(distinct visit_id),
       '', ''
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and created_at > now() - interval '30 days';

select 'last_7d',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
       count(distinct visit_id),
       '', ''
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and created_at > now() - interval '7 days';
SQL

# LRN-0025 (LEARNINGS.md): on 2026-09-29 the last_7d row above read as a rise
# (14/18/50 against 12/14/27) and was written into GOALS.md, STATUS.md and
# three other files as "up on every measure" before anybody checked HOW it
# arrived. 30 of the 50 pageviews and 9 of the visitor ids had landed in one
# 20-minute window (all direct, four different operating systems); excluding
# that single bucket the week was 7/9/20, DOWN, not up. The same shape had
# already happened once before (23 August) and was not checked for either
# time. The learning's own "next action" is to run this concentration check
# alongside the aggregate before any weekly figure goes in a document, not to
# decide by itself whether a bucket is a bot: report both ways and let the
# reader judge, the same way the manual analysis that found it did.
echo "== visitor concentration by 20-minute bucket, last 7 days (top 10) =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select to_char(date_trunc('hour', created_at)
                + (floor(extract(minute from created_at) / 20) * interval '20 min'),
               'YYYY-MM-DD HH24:MI') as bucket_start,
       count(*) filter (where event_type = 1) as pageviews,
       count(distinct session_id) as visitors,
       count(*) filter (where coalesce(referrer_domain, '') = '') as direct_pageviews
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and created_at > now() - interval '7 days'
group by 1
order by visitors desc, pageviews desc
limit 10;
SQL

echo "== last 7 days, raw vs excluding its single busiest 20-minute bucket =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
with bucketed as (
  select date_trunc('hour', created_at)
           + (floor(extract(minute from created_at) / 20) * interval '20 min') as bucket,
         event_type, session_id, visit_id
  from website_event
  where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
    and created_at > now() - interval '7 days'
),
busiest as (
  select bucket
  from bucketed
  group by bucket
  order by count(distinct session_id) desc
  limit 1
)
select 'raw_week' as basis,
       count(*) filter (where event_type = 1) as pageviews,
       count(distinct session_id) as visitors,
       count(distinct visit_id) as visits
from bucketed
union all
select 'ex_busiest_bucket',
       count(*) filter (where event_type = 1) as pageviews,
       count(distinct session_id) as visitors,
       count(distinct visit_id) as visits
from bucketed
where bucket <> (select bucket from busiest);
SQL

echo "== top pages, last 30 days =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select url_path, count(*) as views
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and event_type = 1
  and created_at > now() - interval '30 days'
group by url_path
order by views desc
limit 8;
SQL

echo "== referrers, last 30 days =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select coalesce(nullif(referrer_domain, ''), '(direct)') as src, count(*) as n
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and event_type = 1
  and created_at > now() - interval '30 days'
group by src
order by n desc
limit 8;
SQL

echo "== custom events, all time =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select event_name, count(*) as n, count(distinct session_id) as visitors
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and event_type = 2
group by event_name
order by n desc;
SQL

echo "== event payloads, all time (the join that used to come back empty) =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select e.event_name,
       d.data_key,
       coalesce(d.string_value, d.number_value::text, d.date_value::text) as value,
       count(*) as n
from website_event e
join event_data d on d.website_event_id = e.event_id
where e.website_id = :'w' and not starts_with(coalesce(e.url_path, ''), '/__')
group by 1, 2, 3
order by 1, 2, 4 desc;
SQL

echo "== scroll depth by page type (EXP-002) =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select coalesce(ty.string_value, '(no type)') as page_type,
       de.string_value as depth,
       count(*) as n
from website_event e
join event_data de on de.website_event_id = e.event_id and de.data_key = 'depth'
left join event_data ty on ty.website_event_id = e.event_id and ty.data_key = 'type'
where e.website_id = :'w' and not starts_with(coalesce(e.url_path, ''), '/__')
  and e.event_name = 'scroll-depth'
group by 1, 2
order by 1, 2;
SQL

echo "== buy clicks, one row each (EXP-001) =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select to_char(e.created_at, 'YYYY-MM-DD HH24:MI') as when,
       left(e.session_id::text, 8) as visitor,
       e.url_path,
       coalesce(pl.string_value, '') as payment_link,
       coalesce(sk.string_value, '') as sku,
       coalesce(s.browser, '') || ' ' || coalesce(s.screen, '') as device
from website_event e
left join event_data pl on pl.website_event_id = e.event_id and pl.data_key = 'plink'
left join event_data sk on sk.website_event_id = e.event_id and sk.data_key = 'sku'
left join session s on s.session_id = e.session_id
where e.website_id = :'w' and not starts_with(coalesce(e.url_path, ''), '/__')
  and e.event_name = 'buy-click'
order by e.created_at;
SQL

echo "== per-session breakdown, last 30 days (PAGEVIEWS vs ALL EVENTS) =="
# WHY THIS BLOCK EXISTS, WRITTEN DOWN SO THE UNITS ARE NEVER MIXED AGAIN
# -------------------------------------------------------------------
# On 2026-09-16 a session read the noise in this data as "one session
# carrying 792 of 947 pageviews (84%), leaving roughly 155 real events".
# It is not 792 pageviews. 792 is that session's TOTAL EVENTS: 431
# pageviews plus 361 custom events (scroll-depth mostly). 947 was the
# site's pageview count. Subtracting one from the other is mismatched
# units, and it understated real traffic by a factor of three for a day
# in GOALS.md and RISKS.md, the two files work is prioritised from.
# Re-derived 2026-09-17: 949 pageviews total, 431 from that session,
# 518 human. Both columns are printed here, side by side, so that the
# question "pageviews or events?" is never answered from memory again.
# LEARNINGS.md LRN-0015.
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select left(e.session_id::text, 8) as visitor,
       count(*) filter (where e.event_type = 1) as pageviews,
       count(*) as all_events,
       count(distinct e.visit_id) as visits,
       coalesce(s.browser, '?') || '/' || coalesce(s.os, '?')
         || '/' || coalesce(s.device, '?') as agent,
       round(extract(epoch from (max(e.created_at) - min(e.created_at))) / 60)::int
         as span_minutes
from website_event e
left join session s on s.session_id = e.session_id
where e.website_id = :'w' and not starts_with(coalesce(e.url_path, ''), '/__')
  and e.created_at > now() - interval '30 days'
group by 1, s.browser, s.os, s.device
order by pageviews desc
limit 15;
SQL

# WHERE A VISIT CAME FROM WHEN THE REFERRER IS GONE
# ------------------------------------------------
# Added 2026-10-02 with the `?from=` parameters on every generated social
# draft. Until then the only answer to "which channel sent this person" was
# referrer_domain, and LinkedIn referrals stopped dead on 28 September with no
# way to tell "stopped posting" from "still posting, now arriving as direct".
# `(direct)` is 698 of the last 30 days' pageviews, so a channel that works can
# hide in it completely.
#
# url_query is stored by Umami, so this needs no new instrumentation at all,
# only the parameter the drafts now carry: from=li, from=bsky, from=fb, from=x.
# A row here is a visit that can be attributed whatever the client did to the
# referrer header.
echo "== arrivals by tracked ?from= parameter, all time =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select substring(url_query from 'from=([a-z0-9_-]+)') as channel,
       count(distinct session_id) as visitors,
       count(distinct visit_id)   as visits,
       count(*)                   as pageviews,
       min(created_at)::date      as first_seen,
       max(created_at)::date      as last_seen
from website_event
where website_id = :'w' and not starts_with(coalesce(url_path, ''), '/__')
  and event_type = 1
  and url_query ~ 'from=[a-z0-9_-]+'
group by channel
order by visitors desc;
SQL
