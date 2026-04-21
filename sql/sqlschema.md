# 🧠 Kaizen Studio (DevSage) — SQL Schema Explanation

---

## 🚀 Overview

This database schema powers a platform that combines:

* Code analysis (AI-driven)
* Developer marketplace (human fixes)
* Credit-based economy (incentives)

### 🔄 Core Flow

1. Users analyze repositories (spend credits)
2. AI detects issues
3. Issues are posted to a marketplace
4. Developers submit fixes (contributions)
5. Reviews are performed (owner + external)
6. Credits are rewarded based on approvals

---

## 👤 1. Users

### Table: `users`

Stores all platform users.

**Key Fields:**

* `id` → Unique user identifier
* `email`, `username` → Authentication
* `is_verified` → Trust signal
* `created_at` → Account creation time

---

## 💰 2. Credit System

### 🔹 Table: `user_balances`

Stores the **current balance** of each user.

* One row per user
* Fast reads and safe updates

---

### 🔹 Table: `credit_transactions`

Every credit movement is recorded here.

**Examples:**

* +50 → Signup bonus
* -10 → Code analysis
* +10 → Approved contribution

---

### 🔒 Trigger: `apply_credit_transaction`

Ensures safe transactions:

1. Locks user balance (`FOR UPDATE`)
2. Checks if balance is sufficient
3. Updates balance safely
4. Prevents negative balances

---

## 📦 3. Repositories

### Table: `repositories`

Stores user code projects.

**Key Fields:**

* `owner_id` → Repo owner
* `name` → Repository name
* Unique per user

---

## 🤖 4. Analysis System

### Table: `analysis_runs`

Tracks every code analysis request.

**Key Fields:**

* `depth` → quick / standard / detailed
* `status` → queued / running / completed
* `requested_by` → user

---

## 🧑‍💻 5. Marketplace

### Table: `marketplace_items`

Represents issues found by AI.

**Example:**

> “High complexity function — needs refactor”

**Key Fields:**

* `repo_id` → Affected repository
* `title` → Issue summary
* `status` → Lifecycle stage

---

## 🛠️ 6. Contributions

### Table: `contributions`

Represents a developer’s submitted fix.

**Key Fields:**

* `contributor_id`
* `status`
* `credits_issued`

---

## ✅ 7. Approval System

### Table: `contribution_approvals`

Each row represents one review.

**Roles:**

* `owner` → Repo owner
* `external` → Marketplace reviewer

---

### 🔒 Constraints

#### 1. Only ONE external reviewer

```sql
CREATE UNIQUE INDEX one_external_reviewer
ON contribution_approvals (contribution_id)
WHERE role = 'external';
```

---

#### 2. Approved reviews must have timestamps

```sql
CHECK (decision != 'approved' OR reviewed_at IS NOT NULL)
```

---

#### 3. Only repo owner can approve as owner

(Enforced via trigger)

---

#### 4. Daily limit (max 2 approvals per reviewer)

Prevents spam or abuse.

---

## 🎯 8. Finalisation Logic

### Function: `finalise_contribution`

Automatically runs when approvals change.

### ✔ Conditions:

* Owner approves
* External reviewer approves AND is validated

---

### 🎁 Actions:

1. Mark contribution as fully approved
2. Give contributor **+10 credits**
3. Give reviewer **+5 credits**

---

### 🛡️ Safety Feature

```sql
ON CONFLICT DO NOTHING
```

Prevents:

* Duplicate rewards
* Race conditions

---

## ⚡ 9. Automatic Trigger

```sql
AFTER INSERT OR UPDATE ON contribution_approvals
```

Every approval update:
→ triggers finalisation check

---

## 🚀 10. Indexes

Indexes improve performance for:

* Filtering by status
* Dashboard queries
* High-scale usage

---

## 🔄 Full System Flow

### Step 1 — User signs up

→ Receives credits

### Step 2 — Runs analysis

→ Credits deducted
→ `analysis_runs` created

### Step 3 — AI detects issues

→ `marketplace_items` created

### Step 4 — Developer submits fix

→ `contributions` created

### Step 5 — Reviews happen

→ `contribution_approvals` updated

### Step 6 — System evaluates

→ Checks approval conditions

### Step 7 — Rewards issued

* Contributor → +10 credits
* Reviewer → +5 credits

---

## 🧠 Design Strengths

✅ Concurrency-safe credit system
✅ Strong DB-level rule enforcement
✅ Idempotent reward logic
✅ Modular and scalable structure
✅ Real-world production patterns

---

## ⚠️ Future Improvements

* Event-driven architecture (Kafka/SNS)
* Reputation system
* Contribution versioning
* Microservices separation

---

## 🏁 Conclusion

This schema is designed like a **real-world production system**, combining:

* Financial integrity
* Workflow enforcement
* Scalable architecture

It forms the backbone of a **developer ecosystem with incentives and trust built in**.

---
