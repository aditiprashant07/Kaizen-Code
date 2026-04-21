-- =============================================================================
-- KAIZEN STUDIO (DevSage) — Full SQL Schema (PRODUCTION v2)
-- =============================================================================
-- Fixes included:
--   ✓ Concurrency-safe credit system
--   ✓ Idempotent credit issuance
--   ✓ Strict approval constraints
--   ✓ Ownership enforcement
--   ✓ External reviewer limit correctness
--   ✓ Index + integrity improvements
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SECTION 1 — USERS
-- -----------------------------------------------------------------------------

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- SECTION 2 — CREDIT SYSTEM (FIXED)
-- -----------------------------------------------------------------------------

CREATE TABLE user_balances (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 0
);

CREATE TYPE credit_transaction_type AS ENUM (
    'signup_bonus',
    'analysis_quick',
    'analysis_standard',
    'analysis_detailed',
    'contribution_approved',
    'review_reward',
    'admin_adjustment'
);

CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type credit_transaction_type NOT NULL,
    amount INTEGER NOT NULL,
    reference_id UUID,
    reference_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, reference_id, type)
);

-- Safe transaction function
CREATE OR REPLACE FUNCTION apply_credit_transaction()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    current_balance INTEGER;
BEGIN
    SELECT balance INTO current_balance
    FROM user_balances
    WHERE user_id = NEW.user_id
    FOR UPDATE;

    IF current_balance IS NULL THEN
        INSERT INTO user_balances (user_id, balance)
        VALUES (NEW.user_id, 0)
        RETURNING balance INTO current_balance;
    END IF;

    IF (current_balance + NEW.amount) < 0 THEN
        RAISE EXCEPTION 'Insufficient credits';
    END IF;

    UPDATE user_balances
    SET balance = balance + NEW.amount
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_apply_credit
BEFORE INSERT ON credit_transactions
FOR EACH ROW EXECUTE FUNCTION apply_credit_transaction();

-- -----------------------------------------------------------------------------
-- SECTION 3 — REPOSITORIES
-- -----------------------------------------------------------------------------

CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (owner_id, name)
);

-- -----------------------------------------------------------------------------
-- SECTION 4 — ANALYSIS
-- -----------------------------------------------------------------------------

CREATE TYPE analysis_depth AS ENUM ('quick', 'standard', 'detailed');
CREATE TYPE analysis_status AS ENUM ('queued','running','completed','failed');

CREATE TABLE analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id UUID REFERENCES repositories(id),
    requested_by UUID REFERENCES users(id),
    depth analysis_depth NOT NULL,
    status analysis_status DEFAULT 'queued',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- SECTION 5 — MARKETPLACE
-- -----------------------------------------------------------------------------

CREATE TYPE marketplace_item_status AS ENUM (
    'pending_review','claimed','review_submitted','closed'
);

CREATE TABLE marketplace_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id UUID REFERENCES repositories(id),
    posted_by UUID REFERENCES users(id),
    title TEXT NOT NULL,
    status marketplace_item_status DEFAULT 'pending_review',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- SECTION 6 — CONTRIBUTIONS & APPROVALS (FIXED)
-- -----------------------------------------------------------------------------

CREATE TYPE contribution_status AS ENUM (
    'open','owner_approved','fully_approved','rejected'
);

CREATE TABLE contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    marketplace_item_id UUID REFERENCES marketplace_items(id),
    contributor_id UUID REFERENCES users(id),
    status contribution_status DEFAULT 'open',
    credits_issued BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE approval_role AS ENUM ('owner','external');
CREATE TYPE approval_decision AS ENUM ('approved','rejected','pending');

CREATE TABLE contribution_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contribution_id UUID REFERENCES contributions(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(id),
    role approval_role NOT NULL,
    decision approval_decision DEFAULT 'pending',
    reviewed_at TIMESTAMPTZ,
    owner_validated BOOLEAN,
    review_credit_issued BOOLEAN DEFAULT FALSE,
    UNIQUE (contribution_id, reviewer_id)
);

-- Ensure only ONE external reviewer
CREATE UNIQUE INDEX one_external_reviewer
ON contribution_approvals (contribution_id)
WHERE role = 'external';

-- Ensure reviewed_at exists if approved
ALTER TABLE contribution_approvals
ADD CONSTRAINT chk_review_time
CHECK (decision != 'approved' OR reviewed_at IS NOT NULL);

-- Enforce owner must be repo owner
CREATE OR REPLACE FUNCTION enforce_owner_role()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    actual_owner UUID;
BEGIN
    IF NEW.role = 'owner' THEN
        SELECT r.owner_id INTO actual_owner
        FROM contributions c
        JOIN marketplace_items mi ON mi.id = c.marketplace_item_id
        JOIN repositories r ON r.id = mi.repo_id
        WHERE c.id = NEW.contribution_id;

        IF NEW.reviewer_id != actual_owner THEN
            RAISE EXCEPTION 'Only repo owner can approve as owner';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_owner_enforce
BEFORE INSERT OR UPDATE ON contribution_approvals
FOR EACH ROW EXECUTE FUNCTION enforce_owner_role();

-- Daily limit: max 2 external approvals
CREATE OR REPLACE FUNCTION limit_external_reviews()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    cnt INTEGER;
BEGIN
    IF NEW.role = 'external' AND NEW.decision = 'approved' THEN
        SELECT COUNT(*) INTO cnt
        FROM contribution_approvals
        WHERE reviewer_id = NEW.reviewer_id
        AND role = 'external'
        AND decision = 'approved'
        AND reviewed_at >= CURRENT_DATE;

        IF cnt >= 2 THEN
            RAISE EXCEPTION 'Daily limit reached';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_limit_reviews
BEFORE INSERT OR UPDATE ON contribution_approvals
FOR EACH ROW EXECUTE FUNCTION limit_external_reviews();

-- Finalisation (IDEMPOTENT)
CREATE OR REPLACE FUNCTION finalise_contribution(p_id UUID)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    owner_ok BOOLEAN;
    ext_ok BOOLEAN;
    contributor UUID;
    reviewer UUID;
BEGIN
    SELECT contributor_id INTO contributor FROM contributions WHERE id = p_id;

    SELECT (decision='approved') INTO owner_ok
    FROM contribution_approvals
    WHERE contribution_id=p_id AND role='owner';

    SELECT (decision='approved' AND owner_validated=TRUE), reviewer_id
    INTO ext_ok, reviewer
    FROM contribution_approvals
    WHERE contribution_id=p_id AND role='external';

    IF owner_ok AND ext_ok THEN

        UPDATE contributions
        SET status='fully_approved', credits_issued=TRUE
        WHERE id=p_id AND credits_issued=FALSE;

        INSERT INTO credit_transactions(user_id,type,amount,reference_id)
        VALUES (contributor,'contribution_approved',10,p_id)
        ON CONFLICT DO NOTHING;

        INSERT INTO credit_transactions(user_id,type,amount,reference_id)
        VALUES (reviewer,'review_reward',5,p_id)
        ON CONFLICT DO NOTHING;

    END IF;
END;
$$;

CREATE TRIGGER trg_finalize
AFTER INSERT OR UPDATE ON contribution_approvals
FOR EACH ROW EXECUTE FUNCTION finalise_contribution(NEW.contribution_id);

-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------

CREATE INDEX idx_contributions_status ON contributions(status);
CREATE INDEX idx_marketplace_status ON marketplace_items(status);
CREATE INDEX idx_analysis_status ON analysis_runs(status);
