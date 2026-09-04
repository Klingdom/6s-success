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
where website_id = :'w';

select 'last_30d',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
       count(distinct visit_id),
       '', ''
from website_event
where website_id = :'w'
  and created_at > now() - interval '30 days';

select 'last_7d',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
       count(distinct visit_id),
       '', ''
from website_event
where website_id = :'w'
  and created_at > now() - interval '7 days';
SQL

echo "== top pages, last 30 days =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select url_path, count(*) as views
from website_event
where website_id = :'w'
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
where website_id = :'w'
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
where website_id = :'w'
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
where e.website_id = :'w'
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
where e.website_id = :'w'
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
where e.website_id = :'w'
  and e.event_name = 'buy-click'
order by e.created_at;
SQL
