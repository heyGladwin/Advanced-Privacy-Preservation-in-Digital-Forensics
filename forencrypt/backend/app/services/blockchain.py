import hashlib
import json

from sqlalchemy.orm import Session

from app.models.blockchain import BlockchainBlock

GENESIS_HASH = "0" * 64

def generate_block_hash(
    block_index: int,
    evidence_id: int,
    action: str,
    performed_by: int,
    evidence_hash: str,
    previous_hash: str
) -> str:

    block_data = {
        "block_index": block_index,
        "evidence_id": evidence_id,
        "action": action,
        "performed_by": performed_by,
        "evidence_hash": evidence_hash,
        "previous_hash": previous_hash
    }

    block_string = json.dumps(
        block_data,
        sort_keys=True
    )

    return hashlib.sha256(
        block_string.encode("utf-8")
    ).hexdigest()


def create_block(
    db: Session,
    evidence_id: int,
    action: str,
    performed_by: int,
    evidence_hash: str
):

    # Get the latest block
    latest_block = db.query(
        BlockchainBlock
    ).order_by(
        BlockchainBlock.block_index.desc()
    ).first()

    # Genesis block
    if latest_block is None:

        block_index = 1

        previous_hash = GENESIS_HASH

    else:

        block_index = latest_block.block_index + 1

        previous_hash = latest_block.block_hash


    # Generate hash for the new block
    block_hash = generate_block_hash(
        block_index=block_index,
        evidence_id=evidence_id,
        action=action,
        performed_by=performed_by,
        evidence_hash=evidence_hash,
        previous_hash=previous_hash
    )

    # Create blockchain block
    new_block = BlockchainBlock(

        block_index=block_index,

        evidence_id=evidence_id,

        action=action,

        performed_by=performed_by,

        evidence_hash=evidence_hash,

        previous_hash=previous_hash,

        block_hash=block_hash
    )


    db.add(new_block)

    db.commit()

    db.refresh(new_block)

    return new_block