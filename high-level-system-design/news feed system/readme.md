# Facebook News Feed — Staff/Senior-Level System Design


# First: What architecture patterns does News Feed exercise?

Your reusable framework has 16 patterns:

1. Read-heavy / caching
2. Write-heavy / ingestion
3. Partitioning, sharding & hotspot handling
4. Replication, consistency & quorum
5. Event-driven / messaging / stream processing
6. Fanout / aggregation / feed generation
7. Search & indexing
8. Object/blob storage, CDN & media delivery
9. Real-time communication / WebSockets / presence
10. Workflow / scheduling / async jobs
11. Transactions / payments / inventory / reservations
12. Distributed coordination / locking / leader election / consensus
13. Geospatial / proximity / location tracking
14. Analytics / batch / streaming data pipelines
15. Multi-region / HA / DR / global routing
16. Multi-tenancy / rate limiting / quotas / backpressure / overload control

## Primary patterns for News Feed

The **core pattern is #6: Fanout / aggregation / feed generation**.

The next most important are:

| Priority        | Pattern                                    | Why                                                    |
| --------------- | ------------------------------------------ | ------------------------------------------------------ |
| **P0**          | **Fanout / aggregation / feed generation** | Constructing each user's personalized feed             |
| **P0**          | **Read-heavy / caching**                   | Billions of feed reads                                 |
| **P0**          | **Partitioning / sharding / hotspots**     | Users, feeds, graph and celebrity accounts             |
| **P0**          | **Event-driven / stream processing**       | Post → fanout → ranking → notification pipelines       |
| **P0**          | **Consistency / replication**              | Social graph, posts, feed freshness                    |
| **P1**          | **Write-heavy / ingestion**                | Posts, reactions, comments and graph changes           |
| **P1**          | **Multi-region / HA / DR**                 | Global service availability                            |
| **P1**          | **Backpressure / overload control**        | Viral posts and celebrity accounts                     |
| **P1**          | **Object storage / CDN**                   | Photos/videos attached to feed posts                   |
| **P1**          | **Analytics / streaming pipelines**        | Ranking signals and engagement analytics               |
| **P1**          | **Search/indexing**                        | Secondary capability, not the fundamental feed problem |
| **P2**          | Workflow / async jobs                      | Reprocessing, ranking, moderation, repair              |
| **P2**          | Distributed coordination                   | Shard/worker coordination, elections, etc.             |
| **P2**          | Multi-tenancy/rate limiting                | Abuse prevention and protection                        |
| **Not central** | Real-time communication                    | Messenger/Chat is a different primary problem          |
| **Not central** | Geospatial                                 | Not fundamental to the feed                            |
| **Not central** | Transactions/payments                      | Not fundamental to News Feed                           |

### The key reusable insight

If you remember only one thing:

> **News Feed is fundamentally a fanout + aggregation problem under extreme read load, with a hybrid push/pull strategy required because follower distributions are highly skewed.**

That is much more reusable than memorizing "Facebook uses X database."

---

# System-specific vs reusable knowledge

## System-specific

These are primarily News Feed concepts:

* social graph
* personalized timeline
* friend/follower relationships
* feed ranking
* celebrity fanout
* post visibility

## Reusable

These are much more important for your interview preparation:

* hybrid push/pull
* partitioning
* hot-key mitigation
* cache-aside
* event-driven processing
* idempotent consumers
* eventual consistency
* read/write amplification trade-offs
* backpressure
* multi-region replication
* cursor pagination
* materialized views
* asynchronous processing

The **hybrid fanout pattern** is the transferable mental model.

---

# 13. API Design

## Get Feed

```http
GET /v1/feed?cursor=<cursor>&limit=20
```

Response:

```json
{
  "items": [
    {
      "post_id": "p123",
      "author_id": "u42",
      "created_at": "...",
      "text": "...",
      "media": [],
      "engagement": {
        "likes": 123,
        "comments": 12
      }
    }
  ],
  "next_cursor": "..."
}
```

### Why cursor pagination?

Avoid:

```text
?page=100000
```

Offset pagination becomes increasingly expensive and unstable when new posts arrive.

Use a cursor representing something like:

```text
(last_score, last_post_id)
```

or a stable feed position.

---

## Create Post

```http
POST /v1/posts
```

Request:

```json
{
  "text": "Hello",
  "media_ids": [],
  "visibility": "FRIENDS",
  "client_request_id": "abc123"
}
```

### Idempotency

`client_request_id` prevents duplicate posts if the client retries.

---

## Follow

```http
POST /v1/users/{userId}/following
```

The operation should be idempotent.

Repeated:

```text
Follow(A,B)
Follow(A,B)
```

should not produce duplicate relationship edges.

---

## Delete Post

```http
DELETE /v1/posts/{postId}
```

Must verify:

```text
authenticated_user == post.owner
```

---

# 14. Rate limiting

Potential limits:

```text
CreatePost:
    per-user rate limit

GetFeed:
    per-user + IP/device limits

Follow:
    abuse-sensitive rate limit
```

For feed reads, rate limiting should protect the backend rather than unnecessarily punish legitimate burst traffic.

---

# 15. Data Model

## User

```text
User
----
user_id PK
profile_data
created_at
status
```

---

# 16. Social Graph

Conceptually:

```text
Following
---------
follower_id
followee_id
created_at
```

Partition by:

```text
follower_id
```

for:

```text
Who does Alice follow?
```

But fanout needs:

```text
Who follows Bob?
```

Therefore we generally need the reverse adjacency:

```text
Followers
---------
followee_id
follower_id
created_at
```

This is a classic denormalization for distributed systems.

---

# 17. Why duplicate the graph?

Because these are two different access patterns:

```text
A → Who does A follow?
```

and:

```text
B → Who follows B?
```

Trying to force both through one physical representation can create expensive queries.

This is a general principle:

> **Model distributed data around access patterns, not around normalization purity.**

---

# 18. Post Store

Conceptually:

```text
Post
----
post_id
author_id
created_at
text
media_refs
visibility
version
deleted
```

Partition primarily by:

```text
post_id
```

or another distributed post identifier.

We want efficient direct retrieval:

```text
GetPost(post_id)
```

---

# 19. Feed Store

Conceptually:

```text
FeedEntry
---------
user_id
rank_key
post_id
created_at
author_id
```

Partition:

```text
user_id
```

Sort by:

```text
rank_key / timestamp
```

Access pattern:

```text
Get latest N entries for user U
```

This is an excellent fit for a wide-column/key-value store.

---

# 20. Why not SQL for everything?

SQL is excellent when we need:

* relational integrity
* transactions
* complex joins
* structured business logic

But the feed's dominant operation is:

```text
Give me the latest/top N entries for user X.
```

At enormous scale, a distributed key-value/wide-column model optimized around:

```text
user_id → ordered entries
```

is a better fit.

This doesn't mean SQL is "bad."

It means:

> **The physical data model follows the dominant access pattern.**

---

# 21. Read Path

Let's walk through the important path.

```text
Client
  ↓
Load Balancer
  ↓
API Gateway
  ↓
Feed Service
  ↓
Feed Cache
  ↓
Feed Store
  ↓
Candidate IDs
  ↓
Celebrity / pull candidates
  ↓
Ranking
  ↓
Post Cache
  ↓
Post Store if needed
  ↓
Authorization filtering
  ↓
Response
```

---

# 22. Step 1 — Authentication

Gateway validates:

```text
user_id
session/token
device context
```

---

# 23. Step 2 — Feed cache

Try:

```text
feed:{user_id}
```

If the cache contains enough candidate IDs:

```text
cache hit
```

Otherwise:

```text
Feed Store
```

---

# 24. Step 3 — Materialized feed

Suppose:

```text
Feed Store(user=Alice)
```

returns:

```text
P100
P101
P200
P301
...
```

We should not necessarily return those immediately.

The system may need to:

* remove deleted posts
* verify privacy
* merge celebrity content
* retrieve post objects
* rank candidates

---

# 25. Step 4 — Candidate generation

The feed can be viewed as:

```text
Candidate Generation
        ↓
Filtering
        ↓
Ranking
        ↓
Pagination
```

This separation is extremely important.

### Candidate generation

Find potentially relevant posts.

### Filtering

Remove:

* deleted
* inaccessible
* blocked
* policy-invalid

### Ranking

Order candidates.

---

# 26. Step 5 — Post retrieval

Avoid:

```text
20 network calls
```

Use batching:

```text
GetPosts([P1,P2,...P20])
```

and preferably a distributed multi-key batch API.

---

# 27. Step 6 — CDN

For media:

```text
Feed Service
   ↓
media URL
   ↓
CDN
   ↓
Object Storage
```

The feed service should **not stream large videos through its application servers**.

---

# 28. Read-path bottlenecks

Potential bottlenecks:

1. Feed Store
2. Feed cache
3. Ranking service
4. Post store
5. Network fanout
6. celebrity candidate merging

The most dangerous is often **ranking + candidate retrieval**, not simply the database.

---

# 29. Write Path

Now:

```text
Client
 ↓
API Gateway
 ↓
Post Service
 ↓
Validate
 ↓
Post DB
 ↓
PostCreated event
 ↓
Stream
 ↓
Fanout workers
 ↓
Feed Store
```

---

# 30. Post creation

The Post Service validates:

* authentication
* content size
* visibility
* media ownership
* abuse policies

Then persists the post.

---

# 31. The DB/event problem

Consider:

```text
1. Write post to DB
2. Publish PostCreated
```

What if:

```text
DB succeeds
Kafka publish fails
```

Now:

> The post exists, but no fanout event exists.

The feed becomes silently stale.

This is a classic distributed-systems failure.

---

# 32. Transactional Outbox

One solution:

```text
Post DB
 ├── posts
 └── outbox_events
```

Inside one local transaction:

```text
INSERT post
INSERT PostCreated into outbox
COMMIT
```

Then an outbox publisher sends:

```text
outbox → event stream
```

If publishing fails:

```text
retry
```

This guarantees we don't lose the event merely because the process crashed after the DB commit.

---

# 33. CDC alternative

Another approach:

```text
DB
 ↓
CDC
 ↓
Kafka
 ↓
Fanout
```

CDC can make database changes automatically become events.

### Trade-off

CDC reduces application coupling but introduces:

* CDC infrastructure
* schema evolution concerns
* operational complexity
* ordering considerations

For an interview:

> **Transactional outbox is a very understandable correctness-first answer. CDC is attractive at larger organizational scale.**

---

# 34. Fanout Worker

The worker receives:

```text
PostCreated(author=Bob, post=P123)
```

Then:

```text
followers = SocialGraph.getFollowers(Bob)
```

For ordinary authors:

```text
for follower:
    FeedStore.insert(follower, P123)
```

For celebrity authors:

```text
do not materialize 100M entries
```

Instead:

```text
mark P123 available in Bob's timeline
```

and pull it during feed generation.

---

# 35. Idempotency

Suppose the fanout worker processes:

```text
P123
```

then crashes before acknowledging Kafka.

Kafka redelivers:

```text
P123
```

We must safely process it twice.

Use an idempotent key:

```text
(user_id, post_id)
```

with an idempotent insert/upsert.

Then:

```text
insert(Alice,P123)
insert(Alice,P123)
```

produces one logical entry.

This allows:

> **At-least-once messaging + idempotent consumers**

which is generally much easier to operate than pretending we have magical exactly-once end-to-end semantics.

---

# 36. Messaging Architecture

Use an event stream for high-volume asynchronous processing.

Example topics:

```text
post-events
social-graph-events
engagement-events
```

Potential consumers:

```text
Fanout
Ranking Features
Notifications
Analytics
Moderation
Search Indexer
```

This gives us loose coupling.

---

# 37. Queue vs event stream

## Queue

Use when:

```text
one task → one worker group
```

Example:

```text
Generate thumbnail
```

## Event stream

Use when:

```text
one event → many independent consumers
```

Example:

```text
PostCreated
  ├── Fanout
  ├── Analytics
  ├── Search
  ├── Moderation
  └── Notifications
```

News Feed heavily benefits from the second model.

---

# 38. Partitioning the event stream

Potential partition key:

```text
author_id
```

This can preserve ordering for events from a particular author.

But celebrity authors become hot partitions.

Alternative:

```text
hash(author_id + bucket)
```

with additional ordering mechanisms.

This is a classic trade-off:

> **Ordering and even load distribution often pull partition-key design in opposite directions.**

---

# 39. Delivery semantics

Prefer:

**At-least-once delivery**

plus:

**idempotent consumers**

Why not exactly-once?

Because end-to-end exactly-once semantics across:

```text
DB → stream → worker → another DB
```

are expensive and often unnecessary.

We care about:

```text
correct final state
```

rather than:

```text"this message physically executed exactly once"
```

---

# 40. Consumer failure

If worker crashes:

```text
message remains uncommitted
```

and gets redelivered.

If processing succeeds but acknowledgement fails:

```text
message processed twice
```

Idempotency handles it.

---

# 41. Consumer lag

Monitor:

```text
consumer_lag
```

If lag rises:

1. add consumers
2. increase partition parallelism if possible
3. reduce work per event
4. prioritize important events
5. apply backpressure
6. degrade noncritical processing

---

# 42. Poison message

A malformed event repeatedly crashes a worker.

Without protection:

```text
retry
retry
retry
retry
...
```

Use:

```text
retry topic / delayed retry
        ↓
DLQ
```

with bounded retries.

---

# 43. Database Partitioning

## Feed Store

Partition by:

```text
user_id
```

This is intuitive because the dominant read is:

```text
GetFeed(user_id)
```

But it creates a problem.

What happens if one user receives massive traffic?

That's a **hot key**.

---

# 44. Hot user

Suppose a celebrity account itself is requested millions of times.

Mitigation:

* cache aggressively
* replicate read copies
* shard hot user's data
* request coalescing
* local caches
* CDN where applicable

But note:

> A personalized feed itself is user-specific, so CDN caching has limited value compared with object/media caching.

---

# 45. Hot celebrity fanout

This is the more serious problem.

One author:

```text
100M followers
```

cannot synchronously fan out to 100M feed stores.

We solve it with:

```text
celebrity threshold
```

above which:

```text
pull model
```

is used.

Potentially the threshold is dynamic based on:

* follower count
* posting frequency
* current traffic
* fanout backlog
* shard utilization

---

# 46. Resharding

Suppose Feed Store starts with:

```text
100 shards
```

and needs:

```text
1,000 shards
```

We should not simply hash everything differently and move the entire dataset.

Use:

* consistent hashing
* virtual shards
* shard mapping layer
* online migration

For example:

```text
User → virtual shard → physical shard
```

Then move virtual shards incrementally.

---

# 47. Replica lag

Suppose:

```text
Primary
  ↓
Replica
```

and a user creates a post.

Immediately afterward, they request the feed.

If the feed is read from a lagging replica, they may not see their own post.

This violates:

**read-your-writes**

for the user experience.

Solutions include:

* session stickiness
* reading recent writes from primary
* version/timestamp fencing
* short-lived write cache
* monotonic read tokens

We don't need global strong consistency.

---

# 48. Cross-partition operations

Some operations naturally span partitions:

```text
Get feed
→ posts across many authors
```

We avoid distributed joins.

Instead:

1. retrieve candidate IDs
2. batch fetch post objects
3. merge/rank in application layer

This is a recurring distributed-system pattern:

> **Move expensive joins from the database into controlled application-level aggregation when the query is inherently distributed.**

---

# 49. Caching

## What should we cache?

### Feed candidate lists

```text
feed:{user_id}
```

### Post objects

```text
post:{post_id}
```

### Social graph fragments

```text
followers:{user_id}
following:{user_id}
```

### Ranking features

Potentially short-lived.

---

# 50. Cache strategy

Use:

**cache-aside**

For posts:

```text
GET post
 ↓
cache
 ↓ miss
DB
 ↓
populate cache
```

---

# 51. Feed cache

The feed cache can store:

```text
ordered post IDs
```

rather than entire post objects.

Why?

Because:

* posts can be shared by many users
* post objects have independent invalidation
* feed membership and post content have different lifetimes

This reduces duplication.

---

# 52. TTL

Feed cache:

```text
seconds → minutes
```

depending on freshness requirements.

Post cache:

```text
minutes → hours
```

potentially longer for immutable historical content.

But TTL alone isn't enough.

Deletion/privacy changes require active invalidation or filtering.

---

# 53. Cache invalidation

For post deletion:

```text
PostDeleted
   ├── invalidate post cache
   ├── remove/mark feed entries
   └── update indexes
```

Even if feed-entry deletion is asynchronous, the read path should verify:

```text
is post still visible?
```

for correctness-critical cases.

---

# 54. Cache stampede

Suppose a hot key expires:

```text
1M requests
     ↓
cache miss
     ↓
1M DB requests
```

Mitigations:

* request coalescing
* single-flight
* jittered TTLs
* stale-while-revalidate
* probabilistic early refresh

---

# 55. Cache penetration

Requests for nonexistent posts:

```text
post:not-found
```

could repeatedly hit DB.

Use:

* negative caching
* validation
* rate limiting

---

# 56. Cache avalanche

Large groups of keys expire simultaneously.

Mitigate with:

```text
TTL jitter
```

and gradual refresh.

---

# 57. When should we NOT cache?

Don't cache everything.

Avoid caching data when:

* extremely low reuse
* invalidation cost exceeds benefit
* object is huge
* data is highly sensitive
* freshness requirements are strict
* cache hit rate is predictably poor

Caching is an optimization, not correctness infrastructure.

---

# 58. Consistency Model

Let's explicitly define it.

## Posts

After successful creation:

```text
strong durability
```

but feed propagation is asynchronous.

Therefore:

```text
Post Store = authoritative
Feed = materialized view
```

---

## Feed

Eventually consistent.

A new post may take:

```text
tens/hundreds of milliseconds
```

or longer under overload.

That's acceptable.

---

## Likes

Usually eventual.

We don't need:

```text
global consensus
```

to display:

```text
1,234 likes
```

accurately at every instant.

---

# 59. Privacy is different

Suppose Bob changes a post from:

```text
Friends
```

to:

```text
Only me
```

We cannot say:

> "The feed is eventually consistent, so maybe unauthorized users can see it."

Privacy is a correctness requirement.

We therefore make authorization checks authoritative.

The feed can contain stale **candidates**, but the response must not expose unauthorized content.

---

# 60. Concurrent updates

Suppose:

```text
PostCreated
PostDeleted
```

arrive out of order.

We need versioning:

```text
post_version
```

or timestamps/event sequence numbers.

Consumer logic:

```text
if event.version <= current_version:
    ignore
```

This is safer than assuming event arrival order.

---

# 61. Failure Scenarios

Now we move into Staff-level reasoning.

The source explicitly asks that every major failure be analyzed as:

> Detection → Mitigation → Recovery → Data correctness. 

---

# 62. Feed Service crashes

### Detection

* elevated 5xx
* health checks
* p99 latency

### Mitigation

* load balancer removes unhealthy instances
* traffic routed to healthy instances

### Recovery

* autoscaling/restart

### Data correctness

No persistent feed data is lost because the service is stateless.

---

# 63. Redis/cache failure

### Detection

* cache error rate
* connection failures
* hit rate drops

### Mitigation

Fallback:

```text
Feed Store
```

But this creates a danger:

```text
Redis down
→ all traffic hits DB
→ DB overload
```

Therefore we need:

* admission control
* request throttling
* degraded feeds
* local caches
* gradual recovery

This is a classic **cascading failure** scenario.

---

# 64. Feed database failure

Use:

* replication
* multiple AZs
* automatic failover
* read replicas where appropriate

During partial failure:

```text
serve slightly stale feed
```

rather than failing every request.

---

# 65. Post DB failure

This is more serious because the Post DB is authoritative.

We may:

* reject new posts temporarily
* continue serving cached existing posts
* retry carefully
* fail over to replica/secondary

We should **not acknowledge a post creation unless durability requirements are satisfied.**

---

# 66. Queue failure

If the event stream is unavailable:

```text
Post DB succeeds
Outbox persists event
```

The post remains durable.

Once the stream recovers:

```text
Outbox → stream → fanout
```

This is why the outbox matters.

---

# 67. Fanout worker failure

Messages remain pending.

On recovery:

```text
retry
```

Idempotency prevents duplicate feed entries.

---

# 68. Region failure

With multi-region architecture:

```text
Region A
Region B
Region C
```

Traffic routing moves users away from failed region.

But data architecture determines whether failover is:

* immediate but potentially stale
* or strongly coordinated but slower

For News Feed, we can tolerate some eventual consistency.

---

# 69. Network partition

Suppose:

```text
Feed Service ↔ Feed Store
```

becomes unreliable.

Do not endlessly retry.

Otherwise:

```text
timeouts
 ↓
retries
 ↓
more traffic
 ↓
more saturation
 ↓
timeouts
```

This is retry amplification.

Use:

* deadlines
* bounded retries
* exponential backoff
* jitter
* circuit breakers
* load shedding

---

# 70. Retry storm

A downstream service becomes slow.

Every caller retries.

Traffic becomes:

```text
100K requests
→ 300K attempts
→ 900K attempts
```

Potentially catastrophic.

Staff-level answer:

> **Retries must be budgeted as part of the system's total load, not treated as free reliability.**

---

# 71. Backpressure and overload

The biggest hotspots are:

### 1. Celebrity posts

```text
one write → millions of potential recipients
```

### 2. Viral content

Millions of users simultaneously request the same post/media.

### 3. Ranking service

Every feed request may invoke ranking.

### 4. Fanout backlog

A sudden posting spike produces huge asynchronous work.

---

# 72. Admission control

Under overload, don't necessarily process everything.

Prioritize:

```text
feed reads
post creation
authorization
```

over:

```text
analytics
secondary counters
historical ranking refresh
```

This is **graceful degradation**.

---

# 73. Load shedding

Possible degradation hierarchy:

### Normal

```text
20 candidates
full ranking
fresh counters
```

### Moderate overload

```text
10 candidates
cached ranking
stale counters
```

### Severe overload

```text
precomputed chronological feed
minimal metadata
```

The system remains useful.

---

# 74. Multi-region architecture

A reasonable architecture:

```text
                    Global DNS / Anycast
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Region A      Region B      Region C
             │             │             │
          Feed/API       Feed/API       Feed/API
             │             │             │
          Local cache   Local cache   Local cache
             │             │             │
             └────────── Replicated Data ────────┘
```

---

# 75. Active-active vs active-passive

## Active-active

All regions serve traffic.

### Pros

* better latency
* higher availability
* efficient resource utilization

### Cons

* conflict resolution
* replication complexity
* harder operational model

---

## Active-passive

One region serves writes.

### Pros

* simpler consistency
* simpler operational model

### Cons

* failover latency
* capacity underutilization
* higher cross-region latency

For a massive social network:

> **Active-active is attractive, but the exact consistency strategy varies by datastore and data domain.**

---

# 76. RPO/RTO

Example target:

```text
RPO: seconds/minutes depending on data
RTO: minutes
```

The important point in an interview is not claiming arbitrary "zero RPO."

Instead:

> Different data classes can have different RPO/RTO requirements.

For example:

```text
Post content:
very low RPO

Analytics:
higher RPO acceptable

Feed materialization:
can be rebuilt
```

That last distinction is extremely valuable.

---

# 77. Materialized feed as rebuildable state

This is a powerful design insight.

The feed store isn't necessarily the source of truth.

We have:

```text
Authoritative:
Posts
Social Graph
Permissions

Derived:
Feed materialization
Ranking features
Caches
```

If the feed store is corrupted:

```text
rebuild from source data + events
```

This is a much stronger architecture than treating every derived table as authoritative.

---

# 78. Observability

## Metrics

### Feed

* feed QPS
* p50/p95/p99 latency
* cache hit rate
* candidate count
* ranking latency
* empty-feed rate

### Fanout

* events/sec
* fanout operations/sec
* worker utilization
* queue depth
* consumer lag
* retry rate
* DLQ rate

### Database

* CPU
* memory
* disk utilization
* read/write latency
* connection count
* hot partitions
* replica lag

### Cache

* hit ratio
* eviction rate
* memory usage
* hot keys
* miss latency

---

# 79. Logs

Every request should have:

```text
request_id
trace_id
user_id/hash
service
region
latency
status
dependency results
```

Don't log sensitive content unnecessarily.

---

# 80. Distributed tracing

Trace:

```text
Client
 ↓
Gateway
 ↓
Feed Service
 ├── Feed Cache
 ├── Feed Store
 ├── Ranking
 ├── Post Cache
 └── Authorization
```

This lets us answer:

> Why did p99 feed latency increase?

rather than merely:

> Feed Service is slow.

---

# 81. SLI / SLO

Potential SLO:

```text
99.99% successful feed reads
```

and:

```text
99% feed requests < 300 ms
```

Potential SLIs:

* availability
* latency
* freshness
* correctness

### Error budget

If SLO is:

```text
99.99%
```

we have approximately:

```text
0.01%
```

failure budget.

Engineering teams can spend this budget on:

* deployments
* migrations
* experimentation

rather than blindly optimizing every component.

---

# 82. Security

## Authentication

OAuth/session/token based authentication.

---

## Authorization

Every post retrieval ultimately needs:

```text
Can viewer V see post P?
```

Potential inputs:

* author relationship
* privacy setting
* block relationship
* group membership
* page permissions

---

# 83. Service-to-service authentication

Use:

* mTLS/service identity
* short-lived credentials
* authorization policies

Do not allow arbitrary internal services to access every user's data.

---

# 84. Data privacy

Protect:

* private posts
* user relationships
* personal data
* behavioral/ranking signals

Encrypt:

```text
in transit
at rest
```

and control access with least privilege.

---

# 85. Abuse prevention

Important because this is a social network:

* spam posting
* bot accounts
* follower manipulation
* scraping
* coordinated abuse
* malicious media
* engagement manipulation

Rate limiting and behavioral detection are part of system reliability as well as security.

---

# 86. Scaling Evolution

This is one of the most important Staff-level sections.

---

## 1× scale

Architecture:

```text
API
 ↓
Post DB
 ↓
Feed DB
 ↓
Redis
 ↓
Kafka
 ↓
Workers
```

A relatively conventional distributed architecture works.

### Bottleneck

Database + basic fanout.

---

# 87. 10× scale

Now:

* shard Post Store
* shard Feed Store
* partition Kafka
* multiple cache clusters
* dedicated ranking service
* asynchronous fanout
* multi-AZ

### Current architecture breaks here because...

A single feed DB cannot handle:

```text
hundreds of thousands QPS
```

### We solve that by...

```text
partitioning by user_id
```

and scaling horizontally.

---

# 88. 100× scale

Now the problem becomes distribution skew.

A naive architecture breaks because:

```text
celebrity users
```

create enormous hotspots.

### We solve that by:

```text
hybrid fanout
```

plus:

* hot-key replication
* virtual shards
* adaptive fanout
* aggressive caching
* workload isolation

---

# 89. 1000× scale

At this point the architecture isn't merely:

```text
more machines
```

We need workload specialization.

Potential architecture:

```text
                    Global Routing
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
   Region A           Region B           Region C
       │                 │                  │
   Feed API           Feed API            Feed API
       │                 │                  │
   Candidate          Candidate           Candidate
   Service            Service             Service
       │                 │                  │
   Ranking            Ranking             Ranking
       │                 │                  │
   Regional           Regional            Regional
   Materialization    Materialization     Materialization
       │                 │                  │
       └──────── Global event/data layer ──┘
```

We also need:

* separate hot-user workloads
* priority queues
* adaptive replication
* dedicated infrastructure for ranking
* tiered storage
* aggressive derived-state rebuilding

---

# 90. Bottleneck table

| Scale | First bottleneck    | Solution                                      |
| ----- | ------------------- | --------------------------------------------- |
| 1×    | DB/fanout           | basic sharding + async workers                |
| 10×   | Feed reads          | caching + horizontal partitioning             |
| 100×  | celebrity fanout    | hybrid push/pull                              |
| 100×  | hot partitions      | virtual shards/hot-key replication            |
| 1000× | global coordination | regional isolation + asynchronous replication |
| 1000× | ranking compute     | dedicated ranking/candidate services          |
| 1000× | event processing    | partitioned streams + workload isolation      |

---

# 91. Architecture Trade-offs

## Fanout-on-read vs fanout-on-write

|              |      Read |     Write |  Storage | Celebrity handling |
| ------------ | --------: | --------: | -------: | ------------------ |
| Read fanout  | Expensive |     Cheap |      Low | Excellent          |
| Write fanout |     Cheap | Expensive |     High | Terrible           |
| Hybrid       |       Low |  Moderate | Moderate | Excellent          |

### Interview choice

**Hybrid.**

Because follower distribution is highly skewed.

---

# 92. SQL vs NoSQL

### SQL

Pros:

* transactions
* relational model
* strong constraints

Cons:

* horizontal scale can be harder
* feed access pattern doesn't require joins

### Distributed KV/wide-column

Pros:

* predictable key-based access
* horizontal scaling
* high throughput

Cons:

* limited queries
* application-level aggregation
* more denormalization

### Choice

Use a distributed KV/wide-column store for feed materialization.

Use the database technology appropriate to the authoritative data domain rather than forcing one database everywhere.

---

# 93. Kafka vs direct RPC

### Direct RPC

```text
Post → Fanout Service
```

Problems:

* tight coupling
* synchronous failure propagation
* hard to absorb spikes

### Event stream

```text
Post → Event
          ↓
      consumers
```

Pros:

* decoupling
* buffering
* replay
* independent consumers

### Choice

Use event-driven processing for asynchronous derived work.

---

# 94. Redis vs database

Redis is not the source of truth.

Use it for:

```text
low-latency reusable derived state
```

Database:

```text
durable state
```

If Redis disappears:

> We should degrade to the durable layer rather than lose the feed permanently.

---

# 95. Strong consistency vs eventual consistency

Strong consistency everywhere:

### Pros

Simple semantics.

### Cons

* expensive
* lower availability
* higher latency
* unnecessary

Eventual consistency:

### Pros

* scalable
* resilient
* asynchronous

### Cons

* temporary stale state

### Choice

Use:

> **Strong consistency where correctness/security demands it; eventual consistency for derived feed state.**

---

# 96. Staff-Level Deep Dive #1

## Interviewer

> Why don't you simply fan out every post to every follower?

### Strong answer

Because follower count is heavily skewed.

For normal users, fanout-on-write makes reads cheap.

For a celebrity with tens of millions of followers, fanout creates enormous write amplification and hot partitions.

So we use a hybrid model:

```text
normal → push
celebrity → pull
```

### Follow-up

> What happens if a celebrity becomes viral unexpectedly?

### Stronger answer

The threshold shouldn't necessarily be static.

We can use adaptive routing based on:

* follower count
* fanout cost
* event backlog
* observed traffic
* shard utilization

A user can dynamically move between push and pull treatment.

### Weak answer

> Use Kafka and add more consumers.

### Why weak?

Kafka solves asynchronous delivery, not the fundamental computational problem of:

```text
1 post → 100M recipients
```

---

# 97. Staff-Level Deep Dive #2

## Interviewer

> Why is the feed eventually consistent?

### Strong answer

Because feed membership is derived state.

The authoritative objects are:

```text
post
social graph
permissions
```

Feed entries can be rebuilt.

Making every feed update synchronously consistent would significantly increase latency and coupling without improving the user-visible correctness requirement.

### Follow-up

> What about deleted private posts?

### Stronger answer

Authorization is not allowed to become eventually incorrect.

The materialized feed may contain a stale candidate, but the read path must prevent unauthorized content from being returned.

---

# 98. Staff-Level Deep Dive #3

## Interviewer

> Redis goes down. What happens?

### Strong answer

We fall back to Feed Store.

But the important problem is **cache-failure amplification**.

If 100K QPS suddenly hits the DB:

```text
Redis failure
 → cache misses
 → DB saturation
 → DB latency
 → retries
 → more saturation
```

So we need:

* circuit breakers
* request admission
* load shedding
* request coalescing
* degraded responses
* controlled cache recovery

The Staff-level insight is:

> **The fallback path must itself be capacity-tested.**

---

# 99. Staff-Level Deep Dive #4

## Interviewer

> How do you guarantee the post event isn't lost?

### Answer

Use transactional outbox or CDC.

With outbox:

```text
DB transaction:
    post
    outbox event

commit
```

Then independently:

```text
outbox → Kafka
```

Therefore:

```text
DB succeeded + process crashed
```

doesn't lose the event.

---

# 100. Staff-Level Deep Dive #5

## Interviewer

> Why not exactly-once processing?

### Strong answer

Because end-to-end exactly-once semantics across multiple distributed systems are expensive and often don't provide proportional value.

Instead:

```text
at-least-once delivery
+
idempotent writes
+
deduplication keys
```

gives us effectively-once final state for the relevant operations.

---

# 101. Staff-Level Deep Dive #6

## Interviewer

> How do you handle ordering?

We distinguish:

### Required ordering

Events for the same entity may need:

```text
version 10
version 11
version 12
```

Use:

* partitioning
* sequence/version numbers

### Not required

Independent users' posts don't need globally ordered processing.

Never pay for global ordering when local ordering is sufficient.

---

# 102. Staff-Level Deep Dive #7

## Interviewer

> What if one Feed Store shard is hot?

### Answer

First determine whether it's:

```text
hot partition
```

or:

```text
hot key
```

If one user causes the problem:

```text
hot key
```

Mitigations:

* cache
* replicas
* key splitting
* request coalescing

If many users map to the same shard:

```text
hot partition
```

Mitigations:

* virtual shards
* better partition function
* repartitioning

This distinction is extremely useful in interviews.

---

# 103. Failure Injection Scenarios

The source specifically asks for these kinds of scenarios. 

## 1. Traffic increases 20×

Reason:

```text
Is the bottleneck CPU, DB, cache, ranking, or network?
```

Don't immediately add servers.

First identify the saturated resource.

---

## 2. One DB shard reaches 100%

Ask:

```text
hot key or bad partition distribution?
```

Then:

```text
replicate/split/migrate
```

---

## 3. Celebrity becomes viral

Switch/retain:

```text
pull-based fanout
```

and cache heavily.

Do not fan out to millions synchronously.

---

## 4. Kafka consumer lag continuously increases

Calculate:

```text
incoming rate
vs
processing rate
```

If:

```text
incoming > processing
```

the backlog will grow forever.

Scale consumers or reduce processing cost.

---

## 5. Redis goes down

Fallback to DB, but protect DB with:

* admission control
* degraded responses
* rate limiting
* request coalescing

---

## 6. Primary DB fails

Fail over to replica if appropriate.

For writes:

```text
stop acknowledging until durability is established
```

Don't silently lose posts.

---

## 7. Entire region fails

Global routing moves traffic.

Derived feed state can be rebuilt.

Authoritative data must satisfy the selected RPO.

---

## 8. Network between services becomes unreliable

Use:

```text
timeouts
deadlines
bounded retries
circuit breakers
```

Do not use infinite retries.

---

## 9. Downstream ranking becomes 10× slower

Do not allow ranking to take down feed reads.

Use:

```text
timeout
 ↓
fallback ranking
```

For example:

```text
precomputed ranking
or
chronological order
```

---

## 10. Deployment causes partial failures

Use:

* canary
* gradual rollout
* automated rollback
* version-aware compatibility
* feature flags

---

## 11. Message processed twice

Use:

```text
event_id
+
idempotent consumer
```

---

## 12. Event arrives out of order

Use:

```text
entity version / sequence
```

and reject stale events.

---

# 104. A particularly important Staff-level insight: freshness is a budget

We don't need:

```text
every feed update immediately
```

We need:

```text
acceptable freshness under normal load
```

So we can define:

```text
p99 feed freshness < X seconds
```

This allows us to deliberately trade:

```text
freshness
vs
cost
vs
availability
```

during overload.

That is much stronger than simply saying:

> "The feed is eventually consistent."

---

# 105. Another important insight: separate candidate generation from ranking

Many candidates:

```text
1000 potential posts
```

Then rank:

```text
top 100
```

Then return:

```text
top 20
```

We don't want the ranking system to process millions of posts per request.

Therefore:

```text
Fanout/materialization
        ↓
Candidate generation
        ↓
Cheap filtering
        ↓
Ranking
        ↓
Top-K
```

This architecture generalizes directly to recommendation systems.

---

# 106. Pattern Extraction

| Pattern                       | Where Used           | Why                                        | Reusable In                          |
| ----------------------------- | -------------------- | ------------------------------------------ | ------------------------------------ |
| **Read-heavy / caching**      | Feed/post reads      | Reduce DB latency/load                     | Product catalog, profiles, timelines |
| **Write-heavy / ingestion**   | Posts/events         | Absorb writes asynchronously               | Logging, telemetry                   |
| **Sharding / hotspots**       | Feed/social graph    | Horizontal scale                           | Messaging, storage systems           |
| **Replication / consistency** | Posts/feed/graph     | Availability + correctness                 | Most distributed databases           |
| **Event-driven processing**   | PostCreated pipeline | Decouple consumers                         | Notifications, analytics             |
| **Fanout / aggregation**      | Personalized feed    | Convert expensive reads into derived state | Twitter-like feeds, inboxes          |
| **Object storage/CDN**        | Photos/videos        | Cheap large-object delivery                | YouTube, Instagram                   |
| **Workflow/async jobs**       | Fanout/reprocessing  | Move expensive work off request path       | Media processing                     |
| **Analytics pipelines**       | Engagement/ranking   | Generate signals                           | Recommendations                      |
| **Multi-region HA**           | Global feed          | Availability/latency                       | Most global services                 |
| **Backpressure/overload**     | Viral events         | Prevent cascading failure                  | Any high-scale system                |

---

# 107. Which other HLD problems become easier?

If you deeply understand News Feed, these become much easier:

## 1. Twitter/X Timeline

Almost directly:

```text
fanout-on-write
vs
fanout-on-read
```

---

## 2. Instagram Feed

Same core:

```text
candidate generation
→ ranking
→ media retrieval
```

with heavier media/CDN requirements.

---

## 3. LinkedIn Feed

Same architecture, with more emphasis on:

```text
ranking
recommendation
professional graph
```

---

## 4. Notification System

Same:

```text
event
→ subscribers
→ fanout
→ delivery
```

but delivery semantics become central.

---

## 5. YouTube Recommendations

Same candidate-generation/ranking pattern, but less social fanout.

---

## 6. Email Inbox

Materialized views + pagination + indexing + synchronization.

---

## 7. Chat

Fanout and partitioning are still relevant, although the primary problem shifts to:

```text
ordered real-time delivery
```

---

## 8. News Aggregator

Very similar:

```text
ingest
→ normalize
→ index
→ rank
→ serve
```

---

## 9. Activity Feed / Audit Feed

A simpler version of News Feed:

```text
events
→ materialized timeline
```

---

## 10. Recommendation System

The biggest reusable concept:

```text
candidate generation
→ ranking
→ filtering
→ top-K
```

---

# 108. 5-Minute Interview Explanation

If the interviewer says:

> "Design Facebook News Feed."

I'd answer approximately:

> "The core problem is a personalized feed at very high read volume. I'd use a hybrid fanout architecture."
>
> "When a normal user creates a post, we asynchronously fan it out to follower feed stores. That makes feed reads very cheap. However, celebrity users can have millions of followers, so fanout-on-write would create enormous write amplification and hot partitions. For those users we use fanout-on-read, merging their recent posts during feed generation."
>
> "The request path is Client → Gateway → Feed Service → Feed Cache/Feed Store → candidate generation → ranking → Post Cache/Post Store → authorization → response."
>
> "Posts themselves are authoritative data. The feed is derived state and can therefore be eventually consistent and rebuilt. Privacy and authorization, however, are correctness requirements and cannot be sacrificed for eventual consistency."
>
> "Post creation writes to the Post Store and publishes a PostCreated event. To avoid losing the event between database commit and message publication, I'd use a transactional outbox or CDC. Fanout workers consume the event using at-least-once delivery and idempotent writes."
>
> "The primary partition key for materialized feeds is user ID because the dominant query is 'get this user's feed.' I'd use virtual shards and hot-key mitigation for skew."
>
> "Caching is used for feed candidate lists and post objects. Cache failure must not cascade into database failure, so the fallback path needs admission control, circuit breakers, request coalescing and graceful degradation."
>
> "For global availability, I'd deploy across multiple regions/AZs, replicate authoritative data, and treat materialized feeds as rebuildable derived state."
>
> "The major scaling challenge isn't raw post writes. It's the multiplication of writes caused by fanout and the extreme skew introduced by celebrity users. That's why hybrid fanout is the central architectural decision."

That is the **core Staff-level answer**.

---

# 109. 15-Minute Deep Dive

After the basic architecture, proactively discuss:

### 1. Hybrid fanout

```text
push for normal users
pull for celebrities
```

### 2. Feed data model

```text
user_id → ordered post IDs
```

### 3. Partitioning

```text
user_id
+
virtual shards
+
hot-key mitigation
```

### 4. Event pipeline

```text
Post → Outbox → Stream → Fanout
```

### 5. Consistency

```text
authoritative data = stronger
derived feed = eventual
authorization = correctness-critical
```

### 6. Cache failure

Show that you understand cascading failure.

### 7. Multi-region

Discuss:

```text
active-active
vs
active-passive
```

and data-specific RPO/RTO.

---

# 110. 45-Minute Interview Flow

|      Time | Topic                      |
| --------: | -------------------------- |
|   0–3 min | Clarify requirements       |
|   3–6 min | Scale estimation           |
|  6–10 min | High-level architecture    |
| 10–16 min | Fanout strategy            |
| 16–21 min | Data model + partitioning  |
| 21–26 min | Read/write paths           |
| 26–31 min | Consistency + messaging    |
| 31–36 min | Failure/overload scenarios |
| 36–40 min | Multi-region               |
| 40–43 min | Bottlenecks + trade-offs   |
| 43–45 min | Staff-level follow-ups     |

Don't spend 20 minutes drawing boxes.

The interviewer is primarily evaluating:

> **Can you identify the hard problem and make good trade-offs?**

---

# 111. Top 10 Things to Remember

### 1. News Feed is fundamentally a fanout problem.

Not primarily a database problem.

### 2. Reads dominate writes.

Therefore optimize the read path aggressively.

### 3. Fanout-on-write makes reads fast.

But increases write amplification.

### 4. Fanout-on-read makes writes cheap.

But makes reads expensive.

### 5. Hybrid fanout is the key decision.

Normal users → push.

Celebrities → pull.

### 6. Feed state is derived state.

It can be rebuilt.

### 7. Don't confuse eventual consistency with authorization.

Stale candidates are okay.

Unauthorized data is not.

### 8. At-least-once + idempotency is usually enough.

Don't hide behind "exactly once."

### 9. Cache failure can become DB failure.

Always analyze the fallback path.

### 10. Staff-level design is about evolution.

Always ask:

```text
What breaks at 10×?
What breaks at 100×?
What breaks at 1000×?
```

---

# 112. The Core Mental Model

The entire system can ultimately be reduced to:

```text
                   ┌─────────────────────┐
                   │   Social Graph      │
                   └──────────┬──────────┘
                              │
                              ▼
Post ──→ Event ──→ Candidate Generation
                              │
                    ┌─────────┴─────────┐
                    │                   │
               Push/Fanout          Pull/Celebrity
                    │                   │
                    └─────────┬─────────┘
                              ▼
                       Materialized Feed
                              │
                              ▼
                         Feed Request
                              │
                              ▼
                         Candidates
                              │
                              ▼
                           Filter
                              │
                              ▼
                           Rank
                              │
                              ▼
                         Top-K Posts
                              │
                              ▼
                       Cache / Post DB
                              │
                              ▼
                        Client + CDN
```

And the **one Staff-level sentence** I would want you to remember is:

> **"I would treat News Feed as a materialized, eventually consistent view generated from authoritative social-graph and post data, using hybrid fanout to shift work from the latency-sensitive read path to asynchronous processing while avoiding catastrophic write amplification for high-fanout users."**

That sentence captures most of the architecture.
