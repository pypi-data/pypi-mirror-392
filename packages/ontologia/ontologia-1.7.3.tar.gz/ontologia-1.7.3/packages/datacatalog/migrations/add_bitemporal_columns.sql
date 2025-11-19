-- Migration to add bitemporal columns to ObjectInstance and LinkedObject tables
-- This enables full bitemporal queries with valid time and transaction time

-- Add bitemporal columns to ObjectInstance table
ALTER TABLE objectinstance
ADD COLUMN valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN valid_to TIMESTAMP NULL,
ADD COLUMN transaction_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN transaction_to TIMESTAMP NULL;

-- Add indexes for optimal temporal query performance
CREATE INDEX idx_objectinstance_valid_time ON objectinstance (valid_from, valid_to);
CREATE INDEX idx_objectinstance_transaction_time ON objectinstance (transaction_from, transaction_to);

-- Add bitemporal columns to LinkedObject table
ALTER TABLE linkedobject
ADD COLUMN valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN valid_to TIMESTAMP NULL,
ADD COLUMN transaction_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN transaction_to TIMESTAMP NULL;

-- Add indexes for optimal temporal query performance on linked objects
CREATE INDEX idx_linkedobject_valid_time ON linkedobject (valid_from, valid_to);
CREATE INDEX idx_linkedobject_transaction_time ON linkedobject (transaction_from, transaction_to);

-- Drop old unique constraints and replace with temporal ones for ObjectInstance
ALTER TABLE objectinstance DROP CONSTRAINT IF EXISTS uq_objectinstance_ot_pk;
ALTER TABLE objectinstance
ADD CONSTRAINT uq_objectinstance_ot_pk_temporal
UNIQUE (object_type_rid, pk_value, valid_from, transaction_from);

-- Drop old unique constraints and replace with temporal ones for LinkedObject
ALTER TABLE linkedobject DROP CONSTRAINT IF EXISTS uq_linkedobject_unique;
ALTER TABLE linkedobject
ADD CONSTRAINT uq_linkedobject_unique_temporal
UNIQUE (link_type_rid, from_object_rid, to_object_rid, source_pk_value, target_pk_value, valid_from, transaction_from);
