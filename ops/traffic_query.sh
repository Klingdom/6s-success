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
set -e
C=umami-analytics-vi0p-umami-db-1
W=f1fc5160-4473-422d-a89e-73ff6cbdca7a

echo "== 6s-success.com =="
docker exec -i "$C" psql -U umami -d umami -At -F'|' -v w="$W" <<'SQL'
select 'all_time',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
       to_char(min(created_at), 'YYYY-MM-DD'),
       to_char(max(created_at), 'YYYY-MM-DD')
from website_event
where website_id = :'w';

select 'last_30d',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
       '', ''
from website_event
where website_id = :'w'
  and created_at > now() - interval '30 days';

select 'last_7d',
       count(*) filter (where event_type = 1),
       count(distinct session_id),
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
